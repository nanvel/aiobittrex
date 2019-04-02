import asyncio
import hashlib
import hmac
import json
import logging
import time
from base64 import b64decode
from urllib.parse import urlencode
from zlib import decompress, MAX_WBITS

import aiohttp

from aiobittrex import BittrexSocketError, BittrexSocketConnectionClosed, BittrexSocketConnectionError


logger = logging.getLogger(__name__)


class BittrexSocket:
    """
    https://bittrex.github.io/
    """
    SOCKET_URL = 'https://socket.bittrex.com/signalr/'
    SOCKET_HUB = 'c2'

    KEYS = {
        'A': 'ask',
        'a': 'available',
        'B': 'bid',
        'b': 'balance',
        'C': 'closed',
        'c': 'currency',
        'CI': 'cancel_initiated',
        'D': 'deltas',
        'd': 'delta',
        'DT': 'order_delta_type',
        'E': 'exchange',
        'e': 'exchange_delta_type',
        'F': 'fill_type',
        'FI': 'fill_id',
        'f': 'fills',
        'G': 'open_buy_orders',
        'g': 'open_sell_orders',
        'H': 'high',
        'h': 'auto_sell',
        'I': 'id',
        'i': 'is_open',
        'J': 'condition',
        'j': 'condition_target',
        'K': 'immediate_or_cancel',
        'k': 'is_conditional',
        'L': 'low',
        'l': 'last',
        'M': 'market_name',
        'm': 'base_volume',
        'N': 'nonce',
        'n': 'commission_paid',
        'O': 'orders',
        'o': 'order',
        'OT': 'order_type',
        'OU': 'order_uuid',
        'P': 'price',
        'p': 'crypto_address',
        'PD': 'prev_day',
        'PU': 'price_per_unit',
        'Q': 'quantity',
        'q': 'quantity_remaining',
        'R': 'rate',
        'r': 'requested',
        'S': 'sells',
        's': 'summaries',
        'T': 'time_stamp',
        't': 'total',
        'TY': 'type',
        'U': 'uuid',
        'u': 'updated',
        'V': 'volume',
        'W': 'account_id',
        'w': 'account_uuid',
        'X': 'limit',
        'x': 'created',
        'Y': 'opened',
        'y': 'state',
        'Z': 'buys',
        'z': 'pending'
    }

    def __init__(self, api_key=None, api_secret=None, loop=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self._socket_url = None
        self._loop = loop or asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=loop)

    async def close(self):
        await self._session.close()

    @staticmethod
    def _decode(message):
        try:
            deflated_msg = decompress(b64decode(message, validate=True), -MAX_WBITS)
        except SyntaxError:
            deflated_msg = decompress(b64decode(message, validate=True))
        return json.loads(deflated_msg.decode())

    @classmethod
    def replace_keys(cls, d):
        if not isinstance(d, dict):
            return d
        result = {}
        for key, value in d.items():
            key = cls.KEYS.get(key, key)
            if isinstance(value, dict):
                result[key] = cls.replace_keys(value)
            elif isinstance(value, list):
                result[key] = [cls.replace_keys(v) for v in value]
            else:
                result[key] = value
        return result

    async def _get_socket_url(self):
        if self._socket_url is None:
            conn_data = json.dumps([{'name': self.SOCKET_HUB}])
            url = self.SOCKET_URL + 'negotiate' + '?' + urlencode({
                'clientProtocol': '1.5',
                'connectionData': conn_data,
                '_': round(time.time() * 1000)
            })

            async with self._session.get(url) as r:
                socket_conf = await r.json()

            self._socket_url = self.SOCKET_URL.replace('https', 'wss') + 'connect' + '?' + urlencode({
                'transport': 'webSockets',
                'clientProtocol': socket_conf['ProtocolVersion'],
                'connectionToken': socket_conf['ConnectionToken'],
                'connectionData': conn_data,
                'tid': 3
            })

        return self._socket_url

    async def create_ws(self):
        return await self._session.ws_connect(await self._get_socket_url())

    async def _listen(self, endpoint, messages, ws=None):
        ws = ws or await self.create_ws()

        for n, m in enumerate(messages, start=1):
            await ws.send_str(json.dumps({
                'H': self.SOCKET_HUB,
                'M': endpoint,
                'A': m,
                'I': n
            }))

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                decoded_message = json.loads(msg.data)
                if 'E' in decoded_message:
                    raise BittrexSocketError(decoded_message['E'])
                yield decoded_message
            elif msg.type == aiohttp.WSMsgType.closed:
                logger.warning('Websocket connection closed: %s', msg)
                raise BittrexSocketConnectionClosed
            elif msg.type == aiohttp.WSMsgType.error:
                logger.error('Websocket connection error: %s', msg)
                raise BittrexSocketConnectionError
            else:
                logger.warning("Message: {}".format(msg.type))

    async def _get_auth_context(self, ws):
        async for m in self._listen(endpoint='GetAuthContext', messages=[[self.api_key]], ws=ws):
            if 'R' in m:
                return m['R']

    async def listen_account(self, ws=None):
        """Listen to account balance and orders updates

        callbacks:
        uB - balance delta
        uO - order delta
        """
        challenge = await self._get_auth_context(ws)
        signature = hmac.new(
            key=self.api_secret.encode(),
            msg=challenge.encode(),
            digestmod=hashlib.sha512
        ).hexdigest()
        async for m in self._listen(endpoint='Authenticate', messages=[[self.api_key, signature]], ws=ws):
            if 'R' in m:
                assert m['R']

            for row in m.get('M') or []:
                if row['M'] not in ('uB', 'uO'):
                    continue
                for a in row['A']:
                    yield self.replace_keys(self._decode(a))

    async def get_market(self, markets):
        """
        {
            "BTC-TRX": {
                "market_name": null,
                "nonce": 11333,
                "buys": [{
                    "quantity": 428996.57288094,
                    "rate": 8.65e-06
                }],
                "sells": [{
                    "quantity": 91814.92314615,
                    "rate": 8.66e-06
                }],
                "fills": [{
                    "id": 5020055,
                    "time_stamp": 1524904823903,
                    "quantity": 34413.0,
                    "price": 8.66e-06,
                    "total": 0.29801658,
                    "fill_type": "FILL",
                    "order_type": "BUY"
                }]
            }
        }
        """
        result = {}
        async for m in self._listen(endpoint='QueryExchangeState', messages=[[m] for m in markets]):
            if 'R' not in m:
                continue
            i = int(m['I'])
            result[markets[i - 1]] = self.replace_keys(self._decode(m['R']))
            if len(result) >= len(markets):
                break
        return result

    async def listen_market(self, markets, ws=None):
        """Listen to market updates

        callbacks:
        - uE - market delta

        {
            "market_name": "BTC-TRX",
            "nonce": 11919,
            "buys": [],
            "sells": [{
                "type": 2,
                "rate": 8.7e-06,
                "quantity": 197473.52148216
            }],
            "fills": [{
                "order_type": "BUY",
                "rate": 8.7e-06,
                "quantity": 28376.84449489,
                "time_stamp": 1524905878547
            }]
        }
        """
        async for m in self._listen(endpoint='SubscribeToExchangeDeltas', messages=[[m] for m in markets], ws=ws):
            for row in m.get('M') or []:
                if row['M'] != 'uE':
                    continue
                for a in row['A']:
                    yield self.replace_keys(self._decode(a))

    async def get_summary(self):
        """
        {
            "nonce": 5108,
            "summaries": [{
                "market_name": "BTC-ADA",
                "high": 3.388e-05,
                "low": 3.116e-05,
                "volume": 45482116.6444527,
                "last": 3.337e-05,
                "base_volume": 1481.80378307,
                "time_stamp": 1524907023543,
                "bid": 3.333e-05,
                "ask": 3.337e-05,
                "open_buy_orders": 5195,
                "open_sell_orders": 15219,
                "prev_day": 3.118e-05,
                "created": 1506668518873
            }]
        }
        """
        async for m in self._listen(endpoint='QuerySummaryState', messages=['']):
            if 'R' in m:
                return self.replace_keys(self._decode(m['R']))

    async def listen_summary_light(self, ws=None):
        """
        callbacks:
        - uL - light summary delta

        {
            "deltas": [{
                "market_name": "BTC-ADT",
                "last": 7.37e-06,
                "base_volume": 118.05
            }]
        }
        """
        async for m in self._listen(endpoint='SubscribeToSummaryLiteDeltas', messages=[''], ws=ws):
            for row in m.get('M') or []:
                if row['M'] != 'uL':
                    continue
                for a in row['A']:
                    yield self.replace_keys(self._decode(a))

    async def listen_summary(self, ws=None):
        """
        callbacks:
        - uS - summary delta

        {
            "nonce": 5069,
            "deltas": [{
                "market_name": "BTC-ETH",
                "high": 0.07371794,
                "low": 0.071695,
                "volume": 9535.44197173,
                "last": 0.07318011,
                "base_volume": 695.21677418,
                "time_stamp": 1524907827823,
                "bid": 0.07318011,
                "ask": 0.07346991,
                "open_buy_orders": 4428,
                "open_sell_orders": 3860,
                "prev_day": 0.07188519,
                "created": 1439542944817
            }]
        }
        """
        async for m in self._listen(endpoint='SubscribeToSummaryDeltas', messages=[''], ws=ws):
            for row in m.get('M') or []:
                if row['M'] != 'uS':
                    continue
                for a in row['A']:
                    yield self.replace_keys(self._decode(a))
