from twilio.rest import Client
from flask import Flask, request
from configparser import ConfigParser
from bin.inf.weather import Weather
import pymysql.cursors
import threading
from sys import stdout as std

class Contact:

    def __init__(self, weather, user):
        std.write('#C>> Parsing config...\n')
        self.parser = ConfigParser()
        self.parser.read('./data/config.ini')
        self.sendnumber = self.parser.get('twilioSettings', 'sendNumber')
        self.usernumber = self.parser.get('twilioSettings', 'usernumber')
        self.account_sid = self.parser.get('twilioSettings', 'account_sid')
        self.auth_token = self.parser.get('twilioSettings', 'auth_token')
        self.client = Client(self.account_sid, self.auth_token)
        self.weather = weather
        self.contacts = {}
        self.sms_handler = threading.Thread(target=self.send_recv, name='sms_handler')
        std.write('#C>> Starting SMS contact Process...\n')
        self.sms_handler.start()
        # Initiate SQL connection
        self.contact_database = pymysql.connect(
            host='192.168.10.5',
            user='blake',
            password='some_pass',
            database='AI'
        )
        self.cursor = self.contact_database.cursor()
        self.load_contacts()
        self.user = user
        self.recv_thread = threading.Thread(target=self.send_recv)
        self.recv_thread.start()

    def load_contacts(self):
        std.write('#C>> Loading Contacts to Memory...\n')
        self.contacts = {}
        self.cursor.execute('SELECT * FROM profiles')
        data = self.cursor.fetchall()
        for contact in data:
            self.contacts[contact[0]] = contact[1]

    def send_message(self, body, send_numb):
        std.write('#C>> Sending SMS Text...\n')
        message = self.client.messages.create(
            body=body,
            from_=self.sendnumber,
            to=send_numb
        )
        return message

    def send_recv(self):

        app = Flask(__name__)

        @app.route('/sms', methods=['POST'])
        def sms():
            resp = request.form['Body']
            resp_num = request.form['From']
            if resp:
                self.process_text(resp, resp_num)
            return resp

        app.run()

    def process_text(self, resp, resp_num):
        std.write('#C>> Processing Incoming Text...\n')
        resp = resp.lower()
        if resp_num == self.usernumber:
            if 'weather' in resp:
                self.send_weather()
            elif 'forecast' in resp:
                operator = 'for'
                if operator in resp:
                    resp_split = resp.split(' ')
                    operator_loc = resp_split.index(operator)
                    for n in range(0, operator_loc):
                        resp_split[n] = ""
                    time = ' '.join(resp_split)
                    data = Weather.output_forecast(self.weather, time)
                    self.send_message(data, self.user.user_data['number'])
                    return
            elif 'going' in resp:
                self.send_message(
                    'Okay Blake, i will change youre current location accordingly.'
                )
                resp_split = resp.split(' ')
                operator_location = resp_split.index('to')
                keyword_location = operator_location + 1
                self.user
                self.send_message("Okay Blake ill change your location to {}".format(resp_split[keyword_location]), self.user.user_data['location'])

        elif resp_num != self.usernumber:
            profile = None
            for contact in self.contacts:
                if resp_num in contact:
                    profile = contact
                    break
            if profile is not None:
                foward_msg = 'Message recived from {} |\n {}'.format(profile, resp)
                self.send_message(foward_msg, self.user.user_data['number'])
            elif profile is None:
                foward_msg = 'Message recived from: {} |\n {}'.format(resp_num, resp)
                self.send_message(foward_msg, self.user.user_data['number'])

    def send_weather(self):
        data = Weather.output_weather(self.weather)
        self.send_message(data, self.user.user_data['number'])


