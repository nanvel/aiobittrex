class BittrexError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "BittrexError: {}".format(self.message)


class BittrexSocketError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "BittrexSocketError: {}".format(self.message)


class BittrexSocketConnectionClosed(Exception):
    pass  # TODO clarify error code & message


class BittrexSocketConnectionError(Exception):
    pass  # TODO clarify error code & message
