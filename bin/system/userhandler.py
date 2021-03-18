from bin.system.connection import SQLHandler


class UserHandler:

    def __init__(self, token, SQLhandler):

        self.token = token
        self.username = ''

    def dataInit(self):

