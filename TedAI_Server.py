import threading
# from bin.learning import Learning
from bin.system.voice import Voice
from bin.inf.weather import Weather, temp_out
import win32com.client as wincl
from bin.inf.dictionary import Dictionary, Learning, WordHandle
from bin.system.discovery import Discovery
from bin.inf.usertracking import User
from bin.system.contact import Contact
from bin.system.inputHandling import SpeechRecognition
from nltk.stem import WordNetLemmatizer
from time import sleep
from sys import stdout
from bin.utils import bcolors as clr
import socket
from bin.system.connection import Connection
from bin.system.timeHandler import TimeHandler
from queue import Queue
import concurrent.futures

import nltk

nltk.download('punkt')
nltk.download('wordnet')

'''
Future implementations:
    voice recognition

'''

##################################
# Network Variables
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024  # send 2048 (2kb) a time (as buffer size)
# Import Variables
user = ''
current_weather = ''
voice = ''
response = ''
dictionary = ''
contact = ''
discovery = ''
lang_handler = ''
lemmatizer = WordNetLemmatizer()
userInput = ''
Time = ''
processor = ''
CURRENT_CONNECTIONS = []
####################################
num_threads = 8
threadLimiter = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)


####################################
class ConnectionThread:

    def __init__(self, conn, addr):
        self.conn = Connection()


def connectionThread(conn, addr):
    conn = Connection(conn, addr, user)  # Connection instance
    CURRENT_CONNECTIONS.append([conn, addr])
    handlers = []
    threadLimiter.submit(interactionThread, conn)
    while conn.token is None:  # Wait for Connection token
        continue
    while True:
        data = Connection.wait_for_req(conn)  # Wait for Request
        resp = request_handler(conn, data)
        if resp is not None:
            Connection.transmit(conn, resp)
        else:
            continue
    CURRENT_CONNECTIONS.remove([conn, addr])
    return


def request_handler(conn, data):
    print("request:" + data)
    data = WordHandle.contraction_process(lang_handler, data)  # expand any contractions
    response_code = threadLimiter.submit(SpeechRecognition.determine, response, data)
    response_code = response_code.result()
    try:
        resp = response_handler(response_code, conn)
    except AttributeError:
        data = Connection.req_input(conn, "Im sorry, what was that?")
        data = WordHandle.contraction_process(lang_handler, data)
        response_code = SpeechRecognition.determine(response, data)  # Determine correct action and return response code
        resp = response_handler(response_code.split(' '), conn)
    finally:
        return resp


def interactionThread(conn):
    # check reminders
    while True:
        sleep(960)
        reminder_que = User.loadReminders(user, 'today')
        for reminder in reminder_que:
            current_reminder = User.returnReminder(user, reminder)
            break
        current_reminder = current_reminder.split(' '); current_reminder.insert(0, ":SYSx0:"); ' '.join(current_reminder)
        Connection.transmit(conn, current_reminder)

def response_handler(response_code, conn):
    print("r_code:" + response_code['r_code'])
    if response_code['r_code'] == 'Response_0':
        # continue
        return
    elif response_code['r_code'] == "IR_W00":  # Current weather
        weather = Weather.output_weather(current_weather)
        return weather
    elif response_code['r_code'] == "IR_W01":  # Weather forecast
        weather = Weather.output_forecast(current_weather, 'This Afternoon')
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
        data_initialization()
        return "Data reinitalization complete"
    elif response_code['r_code'] == 'IR_S00':
        response_code.remove('IR_S00')
        search = ' '.join(response_code)
        search = WordHandle.punctuation_removal(lang_handler, search)
        resp = Discovery.net_search(search)
        return resp
    elif response_code['r_code'] == "AR_R00": # set reminder
        cat = Connection.req_input(conn, 'What is this for:')
        User.setReminder(response_code['string'], response_code['time'], cat)
    elif response_code['r_code'] == "IR_R00": #reminder request
        print('reminder Request')
        reminders = User.loadReminders(user, response_code['time'])
        resp = []
        for reminder in reminders:
            strReminder = []
            data = User.returnReminder(user, reminder)
            time = Voice.speechTime(data['time'])
            strReminder.append(time + ":"); strReminder.append(data['reminder_string']); strReminder.append("\n")
            resp.append(' '.join(strReminder))
        resp = ' '.join(resp)
        print(resp)
        return resp
    else:
        resp = Voice.return_response(voice, response_code)
        return resp

    '''

    elif 'good morning' in user_input.split(" "):
        return 'Goodmorning Blake'
    else:
        response = Voice.return_response(voice, user_input)
        return response
    '''


def learning_init_seq():
    print("Initializing Learning Sequence...")
    learning_process = Learning(dictionary)
    Learning.learning(learning_process)


def main():
    global Time
    global processor
    # initialization sequence
    stdout.write(f'{clr.OKGREEN}#sys>>Initializing Time Service...{clr.ENDC}\n')
    Time = TimeHandler()
    stdout.write(f'{clr.OKGREEN}=======Starting Data Initialization Sequence======={clr.ENDC}\n')
    data_initialization()
    stdout.write(f'{clr.OKGREEN}=======Starting Systems Initialization Sequence======={clr.ENDC}\n')
    systems_initialization()
    secondary_initialization()
    stdout.write(f'{clr.OKGREEN}==== All Systems Successfully Initialized ===={clr.ENDC}\n')
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(100)
    stdout.write(f"Listening as {SERVER_HOST}:{SERVER_PORT} ...\n")
    current_connections = {}
    while True:
        conn, addr = s.accept()
        threadLimiter.submit(connectionThread, conn, addr)


def data_initialization():
    global user
    global current_weather
    global voice
    global dictionary
    # User data handler instance
    # stdout.write(f'{clr.YELLOW}   {clr.ENDC}\n')
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing User Data Instance...{clr.ENDC}\n')
    sleep(.5)
    user = User(Time)
    # Weather handler instance
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Weather Data Instance...{clr.ENDC}\n')
    sleep(.5)
    current_weather = Weather(user.user_data['blake1'])
    # Dictionary instance
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Dictionary Data...{clr.ENDC}\n')
    sleep(.5)
    dictionary = Dictionary()
    return


def systems_initialization():
    global response
    global discovery
    global lang_handler
    global voice
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Voice Communications System...{clr.ENDC}\n')
    response = SpeechRecognition()
    voice = Voice(dictionary)
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Discovery System...{clr.ENDC}\n')
    discovery = Discovery()
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing Language Handler...{clr.ENDC}\n')
    lang_handler = WordHandle()


def secondary_initialization():
    global contact
    stdout.write(f'{clr.OKBLUE}#sys>> Initializing SMS Communications System...{clr.ENDC}\n')
    contact = Contact(current_weather, user)
    sleep(.5)


main()
