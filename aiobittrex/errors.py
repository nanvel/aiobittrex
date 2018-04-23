class BittrexError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "BittrexError: {}".format(self.message)
