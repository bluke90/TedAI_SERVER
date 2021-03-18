from datetime import datetime, timedelta
import threading
from time import sleep

class TimeHandler:

    def __init__(self):
        self.date_time = datetime.now()
        self.timeUpdateThread = threading.Thread(target=self.update_time)
        self.timeUpdateThread.start()

    @classmethod
    def update_time(cls):
        cls.date_time = datetime.now()

    def return_time(self):
        self.update_time()
        return self.date_time

    def return_dateTime(self):
        self.update_time()
        return self.date_time

    def convert(self, word):
        self.update_time()
        today = self.date_time.replace(microsecond=0, second=0, minute=0, hour=0)
        today = (today + timedelta(days=1))
        tomorrow = (self.date_time + timedelta(hours=24)).replace(microsecond=0, second=0, minute=0, hour=0)
        oneWeek = (self.date_time + timedelta(days=7)).replace(microsecond=0, second=0, minute=0, hour=0)
        twoWeek = (self.date_time + timedelta(days=14)).replace(microsecond=0, second=0, minute=0, hour=0)
        if word == 'today':
            return today
        if word == 'tomorrow':
            return tomorrow

    def getDateRange(self, days):
        today = self.date_time.replace(microsecond=0, second=0, minute=0, hour=0)
        today = [(today + timedelta(hours=x)).replace(microsecond=0, second=0, minute=0) for x in range(24)]
        if days == 0:
            return today
        else:
            dateRange = [(self.date_time + timedelta(days=x)).replace(microsecond=0, second=0, minute=0, hour=0) for x in range(days)]
            return dateRange

    @staticmethod
    def checkDateRange(date, margin):
        if margin == timedelta(days=1):
            if datetime.now() <= date <= datetime.now() + margin:
                return True
            else:
                return False
        else:
            if datetime.now() + timedelta(days=1) <= date <= datetime.now() + margin:
                return True
            else:
                return False


def updateDateTime():
    TimeHandler.update_time()
    return