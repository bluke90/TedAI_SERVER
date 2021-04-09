import requests
from geopy.geocoders import Nominatim
from bin.sysMath.formulas import convert_k_to_f
from sys import stdout as std
from bin.utils import geo_locate, cout

class Weather:
    '''
    notes:
    weather url: https://api.weather.gov/points/32.4618086,-90.1153638

    '''
    # API_KEY = '3c6e735bf5fdb9a6398004edcf295d4a'

    def __init__(self, location):
        cout("#W>> Acquiring geolocation...\n")
        self.location = location; self.geoloc = geo_locate(self.location)
        self.url = 'https://api.weather.gov/points/{},{}'.format(
            self.geoloc[0], self.geoloc[1])
        self.current_weather = {}; self.period_index = []; self.forecast = []
        self.initWeather()


    def initWeather(self):
        self.current_weather = {}; self.period_index = []; self.forecast = []
        std.write("#W>> Retrieving Forecast Data...\n")
        data = self.reqWeather('forecast')
        self.process_weather(data, 'f')
        std.write("#W>> Success, Processing Forecast Data...\n")
        return

    def reqWeather(self, hour_or_forecast):
        if hour_or_forecast == 'forecast':
            req = requests.get(url=self.url)
            data_raw = req.json()
            forcast_url = data_raw['properties']['forecast']
            req = requests.get(url=forcast_url)
            data_raw = req.json()
            return data_raw
        elif hour_or_forecast == 'hour':
            try:
                req = requests.get(url=self.url)
            except:
                std.write("#W>> Error requesting data from weather source")
                req = requests.get(url=self.url)
            data_raw = req.json()
            forcast_url = data_raw['properties']['forecastHourly']
            req = requests.get(url=forcast_url)
            data_raw = req.json()
            return data_raw

    def process_weather(self, data_raw, f_or_c):
        choice = f_or_c
        if choice == 'f':
            try:
                for period in data_raw['properties']['periods']:
                    self.period_index.append(period['name'].lower())
                    self.forecast.append(period['detailedForecast'])
            except KeyError:
                print(data_raw)
                raise KeyError
        elif choice == 'c':
            data = data_raw['properties']['periods'][0]
            # Condition
            self.current_weather['condition'] = data['shortForecast']
            # Temperature
            self.current_weather['temp'] = data['temperature']
            # Wind
            self.current_weather['wind_speed'] = data['windSpeed']
            self.current_weather['wind_direction'] = data['windDirection']

    def output_forecast(self, time):
        if time is int:
            weather = '{}, {}'.format(self.period_index[time], self.forecast[time])
            return weather
        else: time = time.lower()
        if time in self.period_index:
            time = self.period_index.index(time)
            std.write('#W>> Forecast for {}\n'.format(self.period_index[time]))
            return self.forecast[time]
        else:
            std.write('#W>> Forecast for {}\n'.format(self.period_index[0]))
            weather = '{}, {}'.format(self.period_index[0], self.forecast[0])
            return weather

    def output_weather(self):
        try:
            data = self.reqWeather('hour')
            self.process_weather(data, 'c')
        except KeyError:
            std.write("#W>> Error getting weather data\n")
            self.initWeather()
            data = self.reqWeather('hour')
            self.process_weather(data, 'c')
        weather = "Currently: {}, the temperature is: {}, with {}, {} winds.".format(
            self.current_weather['condition'], self.current_weather['temp'],
            self.current_weather['wind_speed'], self.current_weather['wind_direction'])
        return weather


def temp_out(weather_instance):
    weather = weather_instance.current_weather
    temp = weather['temp']
    return temp


'''
    def req_forecast(self):
        req = requests.get(url=self.url)
        data_raw = req.json()
        forcast_url = data_raw['properties']['forecast']
        req = requests.get(url=forcast_url)
        data_raw = req.json()
        return data_raw

    def req_hourly(self):
        req = requests.get(url=self.url)
        data_raw = req.json()
        forcast_url = data_raw['properties']['forecastHourly']
        req = requests.get(url=forcast_url)
        data_raw = req.json()
        return data_raw
'''