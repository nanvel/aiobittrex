import asyncio
import hashlib
import hmac
from asyncio import AbstractEventLoop
from time import time
from typing import Optional, Dict
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientTimeout
from asyncio_throttle import Throttler

from .errors import BittrexResponseError, BittrexApiError, BittrexRestError


class BittrexAPI:
    """API Reference: https://bittrex.github.io/api/v1-1

    https://github.com/ericsomdahl/python-bittrex/blob/master/bittrex/bittrex.py
    """
    API_URL = 'https://bittrex.com/api'

    def __init__(
            self,
            api_key: Optional[str] = None,
            api_secret: Optional[str] = None,
            throttler: Throttler = None,
            loop: AbstractEventLoop = None,
            session: aiohttp.ClientSession = None,
            timeout: int = 20
    ):
        self.api_key = api_key or ''
        self.api_secret = api_secret or ''
        self._loop = loop or asyncio.get_event_loop()
        self._throttler = throttler or self._init_throttler()
        self._session = session or self._init_session(timeout)

    @staticmethod
    def _init_throttler() -> Throttler:
        return Throttler(rate_limit=60, period=60.0)  # https://bittrex.github.io/api/v1-1#call-limits

    def _init_session(self, timeout: int) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            loop=self._loop,
            headers={'Content-Type': 'application/json'},
            timeout=ClientTimeout(total=timeout)
        )

    async def close(self, delay: float = 0.250):
        """Graceful shutdown

        https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        """
        await asyncio.sleep(delay)
        await self._session.close()

    async def _request(self, path, options=None, authenticate=False, version='v1.1'):
        options = options or {}

        if authenticate:
            options.update({
                'apikey': self.api_key,
                'nonce': self._nonce()
            })

        url = self._compose_url(version, path, options)
        headers = {'apisign': self._get_signature(url)} if authenticate else {}

        async with self._throttler:
            async with self._session.get(url=url, headers=headers) as response:
                return await self._handle_response(response)

    @staticmethod
    def _nonce() -> str:
        return f'{int(time() * 1000)}'

    def _compose_url(self, version: str, path: str, options: Dict) -> str:
        result = f'{self.API_URL}/{version}/{path}'
        if options:
            result = f'{result}?{urlencode(options)}'
        return result

    def _get_signature(self, url: str) -> str:
        return hmac.new(
            key=self.api_secret.encode(),
            msg=url.encode(),
            digestmod=hashlib.sha512
        ).hexdigest()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        try:
            response_json = await response.json()
        except aiohttp.ContentTypeError:
            raise BittrexResponseError(response.status, await response.text())
        except Exception as e:
            raise BittrexRestError(e)
        else:
            self._raise_if_error(response_json)
            return response_json['result']

    @staticmethod
    def _raise_if_error(response_json: Dict) -> None:
        if not response_json['success']:
            raise BittrexApiError(response_json.get('message'))

    def get_markets(self):
        """Get the open and available trading markets at Bittrex along with other meta data
        [{
            "MarketCurrency": "LTC",
            "BaseCurrency": "BTC",
            "MarketCurrencyLong": "Litecoin",
            "BaseCurrencyLong": "Bitcoin",
            "MinTradeSize": 0.01441756,
            "MarketName": "BTC-LTC",
            "IsActive": true,
            "Created": "2014-02-13T00:00:00",
            "Notice": null,
            "IsSponsored": null,
            "LogoUrl": "https://bittrexblobstorage.blob.core.windows.net/public/6defbc41-582d-47a6-bb2e-d0fa88663524.png"
        }]
        """
        return self._request(path='public/getmarkets')

    def get_currencies(self):
        """Get all supported currencies at Bittrex along with other meta data
        [{
            "Currency": "BTC",
            "CurrencyLong": "Bitcoin",
            "MinConfirmation": 2,
            "TxFee": 0.0005,
            "IsActive": true,
            "CoinType": "BITCOIN",
            "BaseAddress": "1N52wHoVR79PMDishab2XmRHsbekCdGquK",
            "Notice": null
        }]
        """
        return self._request(path='public/getcurrencies')

    def get_ticker(self, market):
        """Get the current tick values for a market
        {
            "Bid": 0.01702595,
            "Ask": 0.01709242,
            "Last": 0.01702595
        }
        """
        return self._request(path='public/getticker', options={'market': market})

    def get_market_summaries(self):
        """Get the last 24 hour summary of all active markets
        [{
            "MarketName": "BTC-LTC",
            "High": 0.01717,
            "Low": 0.01664,
            "Volume": 19292.05592121,
            "Last": 0.01709242,
            "BaseVolume": 325.65963883,
            "TimeStamp": "2018-04-23T13:09:54.903",
            "Bid": 0.01702596,
            "Ask": 0.01709242,
            "OpenBuyOrders": 1957,
            "OpenSellOrders": 4016,
            "PrevDay": 0.016837,
            "Created": "2014-02-13T00:00:00"
        }]
        """
        return self._request(path='public/getmarketsummaries')

    async def get_market_summary(self, market):
        """Get the last 24 hour summary of a specific market
        {
            "MarketName": "BTC-LTC",
            "High": 0.01717,
            "Low": 0.01664,
            "Volume": 19298.50773759,
            "Last": 0.017092,
            "BaseVolume": 325.76997876,
            "TimeStamp": "2018-04-23T13:12:20.447",
            "Bid": 0.017092,
            "Ask": 0.01709242,
            "OpenBuyOrders": 1957,
            "OpenSellOrders": 4018,
            "PrevDay": 0.01687339,
            "Created": "2014-02-13T00:00:00"
        }
        """
        result = await self._request(path='public/getmarketsummary', options={'market': market})
        if result:
            return result[0]

    def get_order_book(self, market, order_type='both'):
        """Retrieve the orderbook for a given market
        :param order_type: 'buy', 'sell', 'both'
        {
            "buy": [{
                "Quantity": 0.56636808,
                "Rate": 0.01709205
            }],
            "sell": [{
                "Quantity": 67.07309757,
                "Rate": 0.01709242
            }]
        }
        """
        return self._request(
            path='public/getorderbook',
            options={'market': market, 'type': order_type}
        )

    def get_market_history(self, market):
        """Retrieve the latest trades that have occurred for a specific market
        [{
            "Id": 159594115,
            "TimeStamp": "2018-04-23T12:59:56.333",
            "Quantity": 7.08668072,
            "Price": 0.01702576,
            "Total": 0.12065612,
            "FillType": "PARTIAL_FILL",
            "OrderType": "SELL"
        }, {
            "Id": 159594103,
            "TimeStamp": "2018-04-23T12:59:38.147",
            "Quantity": 1.60041657,
            "Price": 0.01709242,
            "Total": 0.02735499,
            "FillType": "FILL",
            "OrderType": "BUY"
        }]
        """
        return self._request(path='public/getmarkethistory', options={'market': market})

    def buy_limit(self, market, quantity, rate):
        """Place a buy order
        {
            "uuid": "614c34e4-8d71-11e3-94b5-425861b86ab6"
        }
        """
        return self._request(
            path='market/buylimit',
            options={'market': market, 'quantity': quantity, 'rate': rate},
            authenticate=True,
        )

    def sell_limit(self, market, quantity, rate):
        """Place a sell order
        {
            "uuid": "614c34e4-8d71-11e3-94b5-425861b86ab6"
        }
        """
        return self._request(
            path='market/selllimit',
            options={'market': market, 'quantity': quantity, 'rate': rate},
            authenticate=True,
        )

    def cancel_order(self, order_id):
        """Cancel a buy or sell order
        """
        return self._request(
            path='market/cancel',
            options={'uuid': order_id},
            authenticate=True
        )

    def get_open_orders(self, market=None):
        """Get open orders, a market can be specified
        [{
            "Uuid": null,
            "OrderUuid": "09aa5bb6-8232-41aa-9b78-a5a1093e0211",
            "Exchange": "BTC-LTC",
            "OrderType": "LIMIT_SELL",
            "Quantity": 5.00000000,
            "QuantityRemaining": 5.00000000,
            "Limit": 2.00000000,
            "CommissionPaid": 0.00000000,
            "Price": 0.00000000,
            "PricePerUnit": null,
            "Opened": "2014-07-09T03:55:48.77",
            "Closed": null,
            "CancelInitiated": false,
            "ImmediateOrCancel": false,
            "IsConditional": false,
            "Condition": null,
            "ConditionTarget": null
        }]
        """
        return self._request(
            path='market/getopenorders',
            options={'market': market} if market else None,
            authenticate=True
        )

    def get_balances(self):
        """Retrieve all balances for the account
        [{
            "Currency": "BSD",
            "Balance": 0.0,
            "Available": 0.0,
            "Pending": 0.0,
            "CryptoAddress": null
        }, {
            "Currency": "BTC",
            "Balance": 6e-08,
            "Available": 6e-08,
            "Pending": 0.0,
            "CryptoAddress": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
        }]
        """
        return self._request(
            path='account/getbalances',
            authenticate=True
        )

    def get_balance(self, currency):
        """Retrieve balance for specific currency
        {
            "Currency": "BTC",
            "Balance": 6e-08,
            "Available": 6e-08,
            "Pending": 0.0,
            "CryptoAddress": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
        }
        """
        return self._request(
            path='account/getbalance',
            options={'currency': currency},
            authenticate=True
        )

    def get_deposit_address(self, currency):
        """Retrieve or generate an address for a specific currency
        {
            "Currency": "BTC",
            "Address": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
        }
        """
        return self._request(
            path='account/getdepositaddress',
            options={'currency': currency},
            authenticate=True
        )

    def withdraw(self, currency, quantity, address):
        """Withdraw funds from the account
        {
            "uuid": "68b5a16c-92de-11e3-ba3b-425861b86ab6"
        }
        """
        return self._request(
            path='account/withdraw',
            options={'currency': currency, 'quantity': quantity, 'address': address},
            authenticate=True
        )

    def get_order(self, order_id):
        """Retrieve a single order by uuid
        {
            "AccountId": null,
            "OrderUuid": "0cb4c4e4-bdc7-4e13-8c13-430e587d2cc1",
            "Exchange": "BTC-SHLD",
            "Type": "LIMIT_BUY",
            "Quantity": 1000.00000000,
            "QuantityRemaining": 1000.00000000,
            "Limit": 0.00000001,
            "Reserved": 0.00001000,
            "ReserveRemaining": 0.00001000,
            "CommissionReserved": 0.00000002,
            "CommissionReserveRemaining": 0.00000002,
            "CommissionPaid": 0.00000000,
            "Price": 0.00000000,
            "PricePerUnit": null,
            "Opened": "2014-07-13T07:45:46.27",
            "Closed": null,
            "IsOpen": true,
            "Sentinel": "6c454604-22e2-4fb4-892e-179eede20972",
            "CancelInitiated": false,
            "ImmediateOrCancel": false,
            "IsConditional": false,
            "Condition": "NONE",
            "ConditionTarget": null
        }
        """
        return self._request(
            path='account/getorder',
            options={'uuid': order_id},
            authenticate=True
        )

    def get_order_history(self, market=None):
        """Retrieve order history
        [{
            "OrderUuid": "fd97d393-e9b9-4dd1-9dbf-f288fc72a185",
            "Exchange": "BTC-LTC",
            "TimeStamp": "2014-07-09T04:01:00.667",
            "OrderType": "LIMIT_BUY",
            "Limit": 0.00000001,
            "Quantity": 100000.00000000,
            "QuantityRemaining": 100000.00000000,
            "Commission": 0.00000000,
            "Price": 0.00000000,
            "PricePerUnit": null,
            "IsConditional": false,
            "Condition": null,
            "ConditionTarget": null,
            "ImmediateOrCancel": false
        }]
        """
        return self._request(
            path='account/getorderhistory',
            options={'market': market} if market else None,
            authenticate=True
        )

    def get_withdrawal_history(self, currency=None):
        """Retrieve the account withdrawal history
        [{
            "PaymentUuid": "88048b42-7a13-4f57-8b7e-109aeeca07d7",
            "Currency": "SAFEX",
            "Amount": 803.7676899,
            "Address": "145J9p6AVjFc2fFV1uyA8d4xweULphyuNv",
            "Opened": "2018-02-20T13:54:41.12",
            "Authorized": true,
            "PendingPayment": false,
            "TxCost": 100.0,
            "TxId": "e1ded8356d2855716ba99ae6b8cbd2c4220a8df15dd37fd7eb29a76dd7a0b1d1",
            "Canceled": false,
            "InvalidAddress": false
        }]
        """
        return self._request(
            path='account/getwithdrawalhistory',
            options={'currency': currency} if currency else None,
            authenticate=True
        )

    def get_deposit_history(self, currency=None):
        """Retrieve the account deposit history
        [{
            "Id": 41565639,
            "Amount": 0.008,
            "Currency": "BTC",
            "Confirmations": 3,
            "LastUpdated": "2017-11-20T16:40:30.6",
            "TxId": "abfec55561b5440b28784dc4b152635c05139f33faec090a3d8e18a8d2c75eec",
            "CryptoAddress": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
        }]
        """
        return self._request(
            path='account/getdeposithistory',
            options={'currency': currency} if currency else None,
            authenticate=True
        )

    # v2.0

    def get_wallet_health(self):
        """View wallets health
        [{
            "Health": {
                "Currency": "BTC",
                "DepositQueueDepth": 0,
                "WithdrawQueueDepth": 24,
                "BlockHeight": 519583,
                "WalletBalance": 0.0,
                "WalletConnections": 8,
                "MinutesSinceBHUpdated": 2,
                "LastChecked": "2018-04-23T13:50:11.827",
                "IsActive": true
            },
            "Currency": {
                "Currency": "BTC",
                "CurrencyLong": "Bitcoin",
                "MinConfirmation": 2,
                "TxFee": 0.0005,
                "IsActive": true,
                "CoinType": "BITCOIN",
                "BaseAddress": "1N52wHoVR79PMDishab2XmRHsbekCdGquK",
                "Notice": null
            }
        }]
        """
        return self._request(
            path='pub/Currencies/GetWalletHealth',
            version='v2.0'
        )

    def get_pending_withdrawals(self, currency=None):
        """Get the account pending withdrawals
        """
        return self._request(
            path='key/balance/getpendingwithdrawals',
            options={'currency': currency} if currency else None,
            authenticate=True,
            version='v2.0'
        )

    def get_pending_deposits(self, currency=None):
        """Get the account pending deposits
        """
        return self._request(
            path='key/balance/getpendingdeposits',
            options={'currency': currency} if currency else None,
            authenticate=True,
            version='v2.0'
        )

    def get_candles(self, market, tick_interval):
        """Get tick candles for market
        Intervals: oneMin, fiveMin, hour, day
        [{
            "O": 0.017059,
            "H": 0.01712003,
            "L": 0.017059,
            "C": 0.017059,
            "V": 49.10766337,
            "T": "2018-04-23T14:07:00",
            "BV": 0.83816494
        }]
        """
        return self._request(
            path='pub/market/GetTicks',
            options={'marketName': market, 'tickInterval': tick_interval},
            version='v2.0'
        )

    async def get_latest_candle(self, market, tick_interval):
        """Get the latest candle for the marke
        {
            "O": 0.017125,
            "H": 0.017125,
            "L": 0.01706,
            "C": 0.017125,
            "V": 2.35065452,
            "T": "2018-04-23T14:09:00",
            "BV": 0.04018997
        }
        """
        result = await self._request(
            path='pub/market/GetLatestTick',
            options={'marketName': market, 'tickInterval': tick_interval},
            version='v2.0'
        )
        if result:
            return result[0]
