import threading
from bin.system.voice import Voice
from bin.inf.weather import Weather
from bin.inf.dictionary import Dictionary, Learning, WordHandle
from bin.system.discovery import Discovery
from bin.system.contact import Contact
from bin.system.inputHandling import SpeechRecognition
from nltk.stem import WordNetLemmatizer
from time import sleep
from sys import stdout
from bin.utils import bcolors as clr
from bin.utils import cout
import socket
from bin.system.connection import Connection
from bin.system.timeHandler import TimeHandler
from queue import Queue
import concurrent.futures
from bin.system.userhandler import UserHandler

'''
Future implementations:
    

'''

##################################
# Network Variables
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024  # send 2048 (2kb) a time (as buffer size)
# Import Variables
voice = None
response = None
dictionary = None
discovery = None
lang_handler = None
userInput = None
Time = None
response_handler = None
lemmatizer = WordNetLemmatizer()
CURRENT_CONNECTIONS = []

####################################
num_threads = 8
threadLimiter = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

####################################


class ResponseHandler:
    RESPONSE_THREADS = 4

    def __init__(self):
        self.req_Q = Queue()
        self.wrkr_initialization()

    def wrkr_initialization(self):
        for thread in range(self.RESPONSE_THREADS):
            cout('#R>> Initializing Response Worker {}...\n'.format(thread))
            wrkr = threading.Thread(target=self.worker, daemon=True)
            wrkr.start()
        return True

    def que_request(self, data, conn, weather, contact, user):
        item = [conn, data, weather, contact, user]
        self.req_Q.put(item)
        return

    def worker(self):
        while True:
            item = self.req_Q.get()
            conn = item[0]; request = item[1]; weather = item[2]; contact = item[3]; user = item[4]
            response_code = self.format_response(request)
            resp = self.gen_response(conn, response_code, weather, contact, user)
            conn.transmit(resp)
            self.req_Q.task_done()

    def format_response(self, data):
        data = WordHandle.contraction_process(lang_handler, data)  # expand any contractions
        response_code = threadLimiter.submit(SpeechRecognition.determine, response, data)
        response_code = response_code.result()
        return response_code

    def gen_response(self, conn, response_code, weather, contact, user):
        cout("#R>> Generating Response for {} | Request: r_code:{}".format(user.username, response_code['r_code']))
        if response_code['r_code'] == 'Response_0':
            # continue
            return
        elif response_code['r_code'] == "IR_W00":  # Current weather
            weather = Weather.output_weather(weather)
            return weather
        elif response_code['r_code'] == "IR_W01":  # Weather forecast
            weather = Weather.output_forecast(weather, 'This Afternoon')
            return weather
        elif response_code['r_code'] == "AR_S00":  # send text

            too = Connection.req_input(conn, "Who would you like to send the text too?")
            too = too.lower()
            if too in contact.contacts:
                too = contact.contacts[too]
            body = Connection.req_input(conn, "what would you like me to say?")
            Contact.send_message(contact, body, too)
            return "Message Sent"
        elif response_code['r_code'] == "IR_D00":  # definition request
            response_code.remove('IR_D00')
            response_code = ' '.join(response_code)
            if response_code is not None:
                return Dictionary.search_word(dictionary, response_code)
            else:
                request_code = Connection.req_input(conn, "What word was that again?")
                return Dictionary.search_word(dictionary, request_code)
        elif response_code['r_code'] == "AR_SYSx0":  # start learning sequence
            learning_init_seq()
        elif response_code['r_code'] == "AR_SYSx1":  # data reinitialization
            return "Data reinitalization complete"
        elif response_code['r_code'] == 'IR_S00':
            response_code.remove('IR_S00')
            search = ' '.join(response_code)
            search = WordHandle.punctuation_removal(lang_handler, search)
            resp = Discovery.net_search(search)
            return resp
        elif response_code['r_code'] == "AR_R00":  # set reminder
            cat = Connection.req_input(conn, 'What is this for:')
            user.setReminder(response_code['string'], response_code['time'], cat)
        elif response_code['r_code'] == "IR_R00":  # reminder request
            print('reminder Request')
            reminders = UserHandler.loadReminders(user, response_code['time'])
            resp = []
            for reminder in reminders:
                strReminder = []
                data = UserHandler.returnReminder(user, reminder)
                time = Voice.speechTime(data['time'])
                strReminder.append(time + ":");
                strReminder.append(data['reminder_string']);
                strReminder.append("\n")
                resp.append(' '.join(strReminder))
            resp = ' '.join(resp)
            print(resp)
            return resp
        else:
            resp = Voice.return_response(voice, response_code)
            return resp


class ConnectionThread:

    def __init__(self, conn, addr):
        self.conn = Connection(conn, addr)
        self.user = UserHandler(self.conn.token)
        self.weather = Weather(self.user.userdata['userdata']['location'])
        self.contact = Contact(self.weather, self.user)
        # self.respHandler = response_handler
        CURRENT_CONNECTIONS.append(self)
        threadLimiter.submit(self.interaction_thread)
        self.req_loop()
        CURRENT_CONNECTIONS.remove(self)

    def req_loop(self):
        cout('#>> User {}, Initialization complete at {}\n'.format(self.user.username, self.conn.addr))
        while True:
            data = self.conn.wait_for_req()
            response_handler.que_request(data, self.conn, self.weather, self.contact, self.user)

    def interaction_thread(self):
        # check reminders
        while True:
            sleep(960)
            reminder_que = self.user.loadReminders('today')
            for reminder in reminder_que:
                current_reminder = self.user.getReminder(reminder)
                break
            current_reminder = current_reminder.split(' ')
            current_reminder.insert(0, ":SYSx0:")
            ' '.join(current_reminder)
            self.conn.transmit(current_reminder)


def learning_init_seq():
    print("Initializing Learning Sequence...")
    learning_process = Learning(dictionary)
    Learning.learning(learning_process)


def main():
    global Time
    # initialization sequence
    stdout.write(f'{clr.OKGREEN}#sys>>Initializing Time Service...{clr.ENDC}\n')
    Time = TimeHandler()
    stdout.write(f'{clr.OKGREEN}=======Starting Data Initialization Sequence======={clr.ENDC}\n')
    stdout.write(f'{clr.OKGREEN}=======Starting Systems Initialization Sequence======={clr.ENDC}\n')
    systems_initialization()
    stdout.write(f'{clr.OKGREEN}==== All Systems Successfully Initialized ===={clr.ENDC}\n')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(100)
    stdout.write(f"Listening as {SERVER_HOST}:{SERVER_PORT} ...\n")
    while True:
        conn, addr = s.accept()
        threadLimiter.submit(ConnectionThread, conn, addr)


def systems_initialization():
    global dictionary
    global response
    global discovery
    global lang_handler
    global voice
    global response_handler
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Dictionary Data...{clr.ENDC}\n')
    dictionary = Dictionary()
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Voice Communications System...{clr.ENDC}\n')
    response = SpeechRecognition()
    voice = Voice(dictionary)
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Discovery System...{clr.ENDC}\n')
    discovery = Discovery()
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Language Handler...{clr.ENDC}\n')
    lang_handler = WordHandle()
    response_handler = ResponseHandler()
    return


if __name__ == '__main__':
    main()
