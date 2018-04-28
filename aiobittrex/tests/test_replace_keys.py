from unittest import TestCase

from aiobittrex.socket import BittrexSocket


class ReplaceKeysTestCase(TestCase):

    def test_replace_keys(self):
        inp = {
            "BTC-TRX": {
                "M": None,
                "N": 10647,
                "Z": [{
                    "Q": 242.46304653,
                    "R": 8.67e-06
                }, {
                    "Q": 417459.77306401,
                    "R": 8.64e-06
                }]
            }
        }

        out = {
            'BTC-TRX': {
                'buys': [{
                    'quantity': 242.46304653,
                    'rate': 8.67e-06
                }, {
                    'quantity': 417459.77306401,
                    'rate': 8.64e-06
                }],
                'market_name': None,
                'nonce': 10647
            }
        }

        self.assertEqual(BittrexSocket.replace_keys(inp), out)
