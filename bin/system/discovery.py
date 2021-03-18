import requests
import json

class Discovery:

    @staticmethod
    def net_search(string):
        string = list(string)
        for n in range(0, len(string)):
            if string[n] == " ":
                string[n] = '+'
        string = ''.join(string)
        url = 'https://api.duckduckgo.com/?q={}&format=json&pretty=1'.format(string)
        req = requests.get(url=url)
        try:
            data_raw = req.json()
            return data_raw['Abstract']
        except json.decoder.JSONDecodeError:
            print('Error net search')
            return 'Unable to pull definition.'
