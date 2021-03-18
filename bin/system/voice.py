import pymysql.cursors
from bin.inf.dictionary import WordHandle, Dictionary
#from google.cloud import speech
from sys import stdout as std
#from bin.system.connection import Connection
from datetime import datetime, time, timedelta

class Voice:

    def __init__(self, dictionary):
        self.resp_database = pymysql.connect(
            host='192.168.10.5',
            user='blake',
            password='some_pass',
            database='AI'
        )
        self.cursor = self.resp_database.cursor()
        self.lang_handler = WordHandle()
        self.dictionary = dictionary
        self.phrases = self.load_phrases()
        # self.client = speech.SpeechClient()


    def load_phrases(self):
        self.cursor.execute("SELECT * FROM responses")
        data = self.cursor.fetchall()
        phrases = []
        for num, line in enumerate(data, start=0):
            phrases.append(self.Phrase(line[1]))
            for keyword in line[0]:
                phrases[num].add_keyword(keyword)

        return phrases


    def return_response(self, body):
        for phrase in self.phrases:
            for keyword in phrase.keywords:
                if keyword in body:
                    phrase.similarities += 1
                else:
                    continue

        max = self.phrases[0]
        for num, phrase in enumerate(self.phrases, start=0):
            if phrase.similarities > max.similarities:
                max = phrase
            else:
                continue

        for phrase in self.phrases:
            phrase.similarities = 0

        return max.phrase

    @staticmethod
    def speechTime(time):
        #curDay = [(time + timedelta(hours=x)).replace(microsecond=0, second=0, minute=0).isoformat() for x in range(24)]
        curWeek = [(time + timedelta(days=x)).replace(microsecond=0, second=0, minute=0, hour=0).isoformat() for x in range(7)]
        #curMonth = [(time + timedelta(weeks=x)).replace(microsecond=0, second=0, minute=0, hour=0, month=0).isoformat() for x in range(4)]
        if time.replace(microsecond=0, second=0, minute=0, hour=0).isoformat() in curWeek:
            strTime = time.strftime("%A %B %d at %I:%M")
            return strTime





    class Phrase:
        def __init__(self, phrase):
            self.similarities = 0
            self.keywords = []
            self.phrase = phrase

        def add_keyword(self, keyword):
            self.keywords.append(keyword)


'''
    def listen(self):
        with sr.Microphone() as source:
            self.r.adjust_for_ambient_noise(source, duration=1)
            std.write('#V>> Listening...\n')
            content = self.r.listen(source)
        raw = content.get_wav_data()
        return self.voice_recognize(raw)

    def voice_recognize(self, raw):
        audio = speech.RecognitionAudio(content=raw)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US"
        )
        std.write('#V>> Recognizing Voice Input...\n')
        response = self.client.recognize(request={"config": config, "audio": audio})
        print(response)
        for result in response.results:
            print(result)
            output = result.alternatives[0].transcript
            break
        return output

    def recording(self):
        with sr.Microphone() as source:
            print('Listening...')
            # self.r.adjust_for_ambient_noise(source, duration=5)
            content = self.r.listen(source)
        print("Stopped listing...")
        raw = content.get_wav_data()
        with open("audio.wav", 'wb') as file:
            file.write(raw)
            file.close()
        return
'''
