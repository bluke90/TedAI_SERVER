import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

class Music:
    def __init__(self):
        # Get username
        self.username = sys.argv[1]
        scope = 'user-read-private user-read-playback-state user-modify-playback-state'
        try:
            self.token = util.prompt_for_user_token(self.username, scope)
        except (AttributeError, JSONDecodeError):
            os.remove(f".cache-{self.username}")
            self.token = util.prompt_for_user_token(self.username, scope)
        # Create Spotify object
        self.spotifyObject = spotipy.Spotify(auth=self.token)
        self.deviceID = self.get_devices()

    def get_devices(self):
        devices = self.spotifyObject.devices()
        print(json.dumps(devices, sort_keys=True, indent=4))
        deviceID = devices['devices'][0]['id']
        return deviceID

    def track_information(self):
        # Get track information
        track = self.spotifyObject.current_user_playing_track()
        print(json.dumps(track, sort_keys=True, indent=4))
        print()
        artist = track['item']['artists'][0]['name']
        track = track['item']['name']

        if artist != "":
            print("Currently playing " + artist + " - " + track)