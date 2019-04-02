class BittrexError(Exception):
    pass


class BittrexRestError(BittrexError):
    pass


class BittrexApiError(BittrexRestError):
    def __init__(self, message):
        self.message = message or 'Unknown error'


class BittrexResponseError(BittrexRestError):
    def __init__(self, status: int, content: str):
        self.status = status
        self.content = content

    def __str__(self) -> str:
        return f'[{self.status}] {self.content!r}'


class BittrexSocketError(BittrexError):
    pass


class BittrexSocketConnectionClosed(BittrexSocketError):
    pass  # TODO: clarify error code & message


class BittrexSocketConnectionError(BittrexSocketError):
    pass  # TODO: clarify error code & message
