import pymysql
from bin.utils import cout
#import TedAI_Server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024  # send 2048 (2kb) a time (as buffer size)

class Connection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.conn.send("Connection Successful...\n".encode())
        self.token = int(self.conn.recv(BUFFER_SIZE).decode())

        # create sql data or load data

    def wait_for_req(self):
        data = self.conn.recv(BUFFER_SIZE).decode()
        return data

    def transmit(self, data):
        return self.conn.send(data.encode())

    def req_input(self, req):
        print('Sending information Request')
        req = ":00x1: " + req
        self.transmit(req)
        return self.wait_for_req()

class SQLConnection:


    def __init__(self):
        self.connectionStatus = self.sqlConnect()

    def sqlConnect(self):
        cout('Attempting Connection to SQL database...\n')
        self.user_database = pymysql.connect(
            host='192.168.10.5',
            user='blake',
            password='some_pass',
            database='AI'); cout('Connection Successful...\n')
        self.cursor = self.user_database.cursor()
        return True

    def execSQL(self, sql, **kwargs):
        if len(kwargs) == 0 or kwargs.get('cursor') == 1:
            cursor = self.cursor
            cursor.execute(sql)
            return cursor
        elif kwargs.get('fetch') == 1 and kwargs.get('dict') == 1:
            cursor = self.user_database.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)
            data = cursor.fetchall()
            if kwargs.get('cursor') == 1:
                return cursor, data
            elif kwargs.get('cursor') == 0 or kwargs.get('cursor') == None:
                return data
        elif kwargs.get('fetchone') == 1 and kwargs.get('dict') == 1:
            cursor = self.user_database.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)
            data = cursor.fetchone()
            if kwargs.get('cursor') == 1:
                return cursor, data
            elif kwargs.get('cursor') == 0 or kwargs.get('cursor') == None:
                return data
        elif kwargs.get('fetch') == 1:
            cursor = self.cursor
            cursor.execute(sql)
            data = cursor.fetchall()
            if kwargs.get('cursor') == 1:
                return cursor, data
            elif kwargs.get('cursor') == False or kwargs.get('cursor') == None:
                return data




