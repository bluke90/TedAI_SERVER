from bin.utils import data_parse
import pymysql.cursors
from geopy.geocoders import Nominatim
from sys import stdout as std
from bin.system.timeHandler import TimeHandler
from datetime import time, datetime, timedelta
from bin.system.connection import SQLConnection
from bin.utils import cout, geo_locate



class User:

    def __init__(self, time):
        self.Time = TimeHandler()
        self.user_data = {}
        self.data_file = 'user.mem'
        self.SQL = SQLHandler()
        cout("#U>> Loading User Data From database...\n")  # !
        self.reminders = {}
        self.load_data()

    def load_data(self):
        cout("#U>> Fetching SQL data...\n")
        cursor, data = self.SQL.execSQL('SELECT * FROM user_index', fetch='all')
        cout("#U>> Loading User Data into Memory...\n")
        for row in data:
            row0 = row[0]
            row1 = row[1]
            self.user_data[row0] = row1
        cout("#U>> Loading User Reminders...\n")
        cursor, data = self.SQL.execSQL('SELECT * FROM blake.reminders', fetch='all')
        for row in data:
            ref_id = row[0]
            cat = row[1]
            time = row[2]
            reminder_string = row[3]
            self.reminders[ref_id] = {'time': time, 'cat': cat, 'reminder_string': reminder_string}

    def update_data(self, field):
        std.write("#U>> Updating User Data Information...\n")
        cursor = self.SQL.execSQL("UPDATE user_index SET 'data' = '{0}' WHERE 'heading' = 'location' LIMIT 1;").__format__(
            field)

    def geo_locate(self):
        geolocator = Nominatim(user_agent="TedAI")
        location = geolocator.geocode(self.user_data['blake1'])
        return location.latitude, location.longitude

    def return_data(self, data):
        if data in self.user_data:
            return self.user_data[data]

    def setReminder(self, data, time, category):
        self.reminders[time] = [category, data]
        self.cursor.execute("INSERT INTO blake.reminders (catagory, time, data) VALUES ('{}', '{}', '{}')".format(category, time, data))
        return 1

    def loadReminders(self, time_period):
        self.load_data()
        days = {'today': 1, 'tomorrow': 2, 'next week': 7}
        output = {}
        for reminder in self.reminders:
            stamp = self.reminders[reminder]['time']; stamp = stamp.replace(microsecond=0, second=0)
            if TimeHandler.checkDateRange(stamp, timedelta(days=days[time_period])):
                output[reminder] = self.reminders[reminder]['time']
        print(output)
        return output

    def returnReminder(self, ref_ID):
        return self.reminders[ref_ID]

















