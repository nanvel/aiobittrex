Bittrex API python async wrapper
================================

Requirements: Python3.6

Installation: ``pip install aiobittrex``

Usage
-----

.. code-block:: python

    import asyncio
    import json

    from aiobittrex import BittrexAPI, BittrexError


    async def main():
        api = BittrexAPI()
        try:
            result = await api.get_markets()
            print(json.dumps(result, indent=2))
        except BittrexError as e:
            print(e)


    if __name__ == '__main__':
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(main())


V1 API
------

``get_markets()``
~~~~~~~~~~~~~~~~~

Get the open and available trading markets at Bittrex along with other meta data.

.. code-block:: json

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

``get_currencies()``
~~~~~~~~~~~~~~~~~~~~

Get all supported currencies at Bittrex along with other meta data.

.. code-block:: json

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

``get_ticker(market)``
~~~~~~~~~~~~~~~~~~~~~~

Get the current tick values for a market.

.. code-block:: json

    {
        "Bid": 0.01702595,
        "Ask": 0.01709242,
        "Last": 0.01702595
    }

``get_market_summaries()``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the last 24 hour summary of all active markets.

.. code-block:: json

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

``get_market_summary(market)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the last 24 hour summary of a specific market.

.. code-block:: json

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

``get_order_book(market, order_type='both')``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve the orderbook for a given market.

Order types:
    - buy
    - sell
    - both

.. code-block:: json

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

``get_market_history(market)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve the latest trades that have occurred for a specific market.

.. code-block:: json

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

``buy_limit(market, quantity, rate)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place a buy order.

.. code-block:: json

    {
        "uuid": "614c34e4-8d71-11e3-94b5-425861b86ab6"
    }

``sell_limit(market, quantity, rate)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place a sell order.

.. code-block:: json

    {
        "uuid": "614c34e4-8d71-11e3-94b5-425861b86ab6"
    }

``cancel_order(order_id)``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Cancel a buy or sell order.

``get_open_orders(market=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get open orders, a market can be specified.

.. code-block:: json

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

``get_balances()``
~~~~~~~~~~~~~~~~~~

Retrieve all balances for the account.

.. code-block:: json

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

``get_balance(currency)``
~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve balance for specific currency.

.. code-block:: json

    {
        "Currency": "BTC",
        "Balance": 6e-08,
        "Available": 6e-08,
        "Pending": 0.0,
        "CryptoAddress": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
    }

``get_deposit_address(currency)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve or generate an address for a specific currency.

.. code-block:: json

    {
        "Currency": "BTC",
        "Address": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
    }

``withdraw(currency, quantity, address)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Withdraw funds from the account.

.. code-block:: json

    {
        "uuid": "68b5a16c-92de-11e3-ba3b-425861b86ab6"
    }

``get_order(order_id)``
~~~~~~~~~~~~~~~~~~~~~~~

Retrieve a single order by uuid.

.. code-block:: json

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

``get_order_history(market=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve order history.

.. code-block:: json

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

``get_withdrawal_history(currency=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve the account withdrawal history.

.. code-block:: json

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

``get_deposit_history(currency=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve the account deposit history.

.. code-block:: json

    [{
        "Id": 41565639,
        "Amount": 0.008,
        "Currency": "BTC",
        "Confirmations": 3,
        "LastUpdated": "2017-11-20T16:40:30.6",
        "TxId": "abfec55561b5440b28784dc4b152635c05139f33faec090a3d8e18a8d2c75eec",
        "CryptoAddress": "1JQts7UT3gYTs31p6k5YGj3qjcRQ6XAXsn"
    }]

V2 API
------

``get_wallet_health()``
~~~~~~~~~~~~~~~~~~~~~~~

View wallets health.

.. code-block:: json

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

``get_pending_withdrawals(currency=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the account pending withdrawals.

``get_pending_deposits(currency=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the account pending deposits.

``get_candles(market, tick_interval)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get tick candles for market.

Intervals:
    - oneMin
    - fiveMin
    - hour
    - day

.. code-block:: json

    [{
        "O": 0.017059,
        "H": 0.01712003,
        "L": 0.017059,
        "C": 0.017059,
        "V": 49.10766337,
        "T": "2018-04-23T14:07:00",
        "BV": 0.83816494
    }]

``get_latest_candle(market, tick_interval)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the latest candle for the market.

.. code-block:: json

    {
        "O": 0.017125,
        "H": 0.017125,
        "L": 0.01706,
        "C": 0.017125,
        "V": 2.35065452,
        "T": "2018-04-23T14:09:00",
        "BV": 0.04018997
    }

Socket
------

Bittrex socket documentation: https://bittrex.github.io/

Usage example:

.. code-block:: python

    from aiobittrex import BittrexSocket


    socket = BittrexSocket()
    market = await socket.get_market(markets=['BTC-ETH', 'BTC-TRX'])
    print(json.dumps(market, indent=2))

    async for m in socket.listen_market(markets=['BTC-ETH', 'BTC-TRX']):
        print(json.dumps(m, indent=2))


```listen_account()```
~~~~~~~~~~~~~~~~~~~~~~

Listen for orders and balances updates for the account.

```get_market(markets)```
~~~~~~~~~~~~~~~~~~~~~~~~~

Get market orders.

.. code-block:: json

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

```listen_market(markets)```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listen for market orders updates.

Delta types:
    - 0 = ADD
    - 1 = REMOVE
    - 2 = UPDATE

.. code-block:: json

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

```get_summary()```
~~~~~~~~~~~~~~~~~~~

Get markets summaries.

.. code-block:: json

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

```listen_summary_light()```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Markets summary updates light.

.. code-block:: json

    {
        "deltas": [{
            "market_name": "BTC-ADT",
            "last": 7.37e-06,
            "base_volume": 118.05
        }]
    }

```listen_summary()```
~~~~~~~~~~~~~~~~~~~~~~

Markets summary updates.

.. code-block:: json

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
