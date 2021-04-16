from bin.system.connection import SQLConnection
from bin.utils import cout, geo_locate
from bin.system.timeHandler import TimeHandler
from datetime import timedelta

class UserHandler:
    """
     User object: Handles the individual data for each user
    """
    def __init__(self, token): # sql time
        """
        Initialize user object
        * class Variables: token, username, userdata<dict>

        :param token:
        """
        cout('#U>> Initializing User Instance...\n')
        self.SQL = SQLConnection()
        self.time = TimeHandler()
        self.token = token
        self.username = None
        self.userdata = {}
        self.dataInit()

    def dataInit(self):
        cout('#U>> Initializing user data...\n')
        data = self.SQL.execSQL("SELECT user FROM ai.user_index WHERE token = {}".format(self.token), fetch=1)
        self.username = data[0][0]
        return self.dataToMemory()

    def dataToMemory(self):
        for table in ['userdata' ,'catwords', 'contacts', 'reminders']:
            cout('#U>> Loading UserData:{} to memory...\n'.format(table))
            if table == 'userdata':
                data = self.SQL.execSQL("SELECT * FROM ai.user_data WHERE token = {}".format(self.token), fetchone=1, dict=1)
            else:
                data = self.SQL.execSQL("SELECT * FROM {}.{}".format(self.username, table), fetch=1)
            self.userdata[table] = data
        return

    def processData(self):
        userdata = self.userdata['userdata']
        catwords = self.userdata['catwords']
        contacts = self.userdata['contacts']
        reminders = self.userdata['reminders']
        # self.userdata = []
        # for data in [userdata, catwords, contacts, reminders]:

    def reloadData(self, table):
        data = self.SQL.execSQL("SELECT * FROM {}.{}".format(self.username, table), fetch=1)
        self.userdata[table] = data
        return

    def loadReminders(self, time_period):
        days = {'today': 1, 'tomorrow': 2, 'next week': 7}
        output = {}
        for reminder in self.userdata['reminders']:
            stamp = self.userdata['reminders'][reminder]['time']; stamp = stamp.replace(microsecond=0, second=0)
            if TimeHandler.checkDateRange(stamp, timedelta(days=days[time_period])):
                output[reminder] = self.userdata['reminders'][reminder]['time']
        return output

    def getReminder(self, red_ID):
        return self.userdata['reminders'][red_ID]

    def setReminder(self, data, time, category):
        self.SQL.execSQL("INSERT INTO blake.reminders (catagory, time, data) VALUES ('{}', '{}', '{}')".format(category, time, data))
        return self.reloadData('reminders')



class Reminders:

    def __init__(self, user):
        self.user = user


