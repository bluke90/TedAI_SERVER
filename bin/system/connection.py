import pymysql
from bin.utils import cout
#import TedAI_Server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024  # send 2048 (2kb) a time (as buffer size)

class Connection:
    def __init__(self, conn, addr, user_instance):
        self.conn = conn
        self.addr = addr
        self.userInstance = user_instance
        self.conn.send("Connection Successful...\n".encode())
        self.token = self.conn.recv(BUFFER_SIZE).decode()
        self.user_data = self.userInstance.user_data[self.token]

        # create sql data or load data

    def wait_for_req(self):
        print('waiting for req')
        data = self.conn.recv(BUFFER_SIZE).decode()
        print('request received')
        return data

    def transmit(self, data):
        return self.conn.send(data.encode())

    def req_input(self, req):
        print('Sending information Request')
        req = ":00x1: " + req
        self.transmit(req)
        return self.wait_for_req()

class SQLHandler:


    def __init__(self):
        self.connectionStatus = self.sqlConnect()

    def sqlConnect(self):
        cout('Attempting Connection to SQL database...')
        self.user_database = pymysql.connect(
            host='192.168.10.5',
            user='root',
            password='some_pass',
            database='AI'
        ); cout('Connection Successful')
        self.cursor = self.user_database.cursor()
        return True

    def execSQL(self, sql, **fetch):
        cursor = self.cursor
        cursor.execute(sql)
        try:
            if fetch['fetch'] == 'all':
                data = cursor.fetchall()
                return cursor, data
        except KeyError:
            return cursor



