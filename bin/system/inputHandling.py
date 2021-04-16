from bin.inf.dictionary import WordHandle as WH
from bin.system.connection import SQLConnection
from bin.system.nlp.languageProcessing import LanguageProcessing
from bin.system.nlp.determineReqType import analyse_intent, init_clf
from bin.system.nlp import determineReqType
from bin.inf.weather import Weather
from bin.system.contact import Contact
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

'''
TOR index:

Information Requests(IR):
    Current Weather: IR_W00
    Weather Forecast: IR_W01
    Definition request: IR_D00
    Get Reminder: "IR_R00"
Action Request(AR):
    Set Reminder:
        Time Given: AR_R00
        Time Not Given: AR_R00x
    Send text:
        without recipitant = AR_S00 
        with recipiant = AR_S01
    initate learning sequence = AR_SYSx0
'''


class SpeechRecognition:
    FEATURE = {
        'weather': ['forecast', 'weather'],
        'learning': ['learning', 'learn'],
        'dictionary': ['definition'],
        'remind': ['remind', 'reminders', 'reminder', 'to do'],
        'sms': ['sms', 'message', 'text']
    }
    # Natural Language Processing
    LP = LanguageProcessing()

    def __init__(self):
        self.SQL = SQLConnection()  # !
        # Array Init
        self.userInput = ''
        """
        self.like_req = {}
        # Get Data From Database : Stack Data to Dict.
        self.rawData = self.SQL.execSQL("SELECT * FROM lang_learning.like_req", fetch=1)
        for row in self.rawData:
            phrases = row[1].split(',')
            self.like_req[row[2]] = phrases
        """

    def determine(self, user_input):
        print(user_input)
        chunks = self.format_input(user_input)
        if chunks['req_type'] == "IR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['weather']: # Weather Feature
                    output = self.determineWeatherReq()
                    code = output['code']
                    code = chunks['req_type'] + code
                    if code == 'IR_W01':
                        time = output['time']
                        resp = {'r_code': code, 'time': time}
                        return resp
                    elif code == 'IR_W00':
                        resp = {'r_code': code}
                        return resp
                elif word in self.FEATURE['dictionary']:
                    output = self.determineDictReq()
                    code = output['code']
                    code = chunks['req_type'] + code
                    resp = {'r_code': code, 'word': output['word']}
                    return resp
                elif word in self.FEATURE['remind']:
                    output = self.determineReminderReq()
                    code = output['code']
                    code = chunks['req_type'] + code
                    resp = {'r_code': code, 'time': output['time']}
                    return resp
        elif chunks['req_type'] == "AR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['sms']:
                    output = self.determineSmsReq()
                    code = output['code']; code = chunks['req_type'] + code
                    if code == 'AR_S01':
                        return {'r_code': code, 'recip': output['recip']}
                    else:
                        return {'r_code': code}
                if word in self.FEATURE['remind']:
                    output = self.determineReminderAct()

    def format_input(self, user_input):
        """
        Format User Input using Natural Language Processing.\n
        Returns: <Dictionary>
            * ['time_chunk'] - Chunk containing date/time information
            * ['intent'] - Chunk containing implied intent
            * ['subject'] - Chunk Containing subject
            * ['req_type'] - Type of request determined by Algorithm\n
        :param user_input: The inputted sentence for processing.
        """
        ref_id = self.LP.queProcessing(user_input)
        chunks = self.LP.completeQ(ref_id=ref_id)
        time_chunk = (chunks['time_chunk'][0])    # list of trees
        intent = (chunks['intent'][0])    # list of trees
        subject = (chunks['subject'][0])  # list of trees
        req_type = analyse_intent(intent)
        return {
            'time_chunk': time_chunk,
            'intent': intent,
            'subject': subject,
            'req_type': req_type
        }
    def determineSmsReq(self):      # DEV
        if 'to' in self.userInput:
            output = {'code': "_S01", 'recip': ''}
            return output
        else:
            return {'code': "_S00"}

    def determineWeatherReq(self):      # DEV
        # what is the weather forecast for tomorrow
        time = None
        for word in self.time_periods:
            if word in self.userInput:
                time = word
        if time:
            return {'code': '_W01', 'time': time}
        elif time is None:
            return {'code': '_W00'}

    def determineDictReq(self):     # DEV
        # what is the definition of ****
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        wordIndex = self.subject.index('IN') + 1
        if dataSplit[wordIndex - 2] == 'definition':
            word = dataSplit[wordIndex]
            return {'code': '_D00', 'word': word}
        else:
            print('error')
            return

    def determineReminderReq(self):     # DEV
        #what do i have to do today
        for word, pos in self.time_chunk:
            if word in self.time_periods:
                time = word
                resp = {'code': '_R00', 'time': time}
                return resp

    def determineReminderAct(self):     # DEV
        print('Dev')

    def phraseMatch(self, string):  # DEV
        elements = []
        for phrase in self.like_req:
            phrase = phrase.split(' ')
            wordCount = 0; removalCount = 0
            for i, word in enumerate(string):
                if word == 'prep':
                    elements.append(string[i + 1])

                if word == phrase[wordCount]:
                    wordCount += 1; removalCount +=1

    def smsHandler(self, packet):
        packet.split('::')
        recip = packet[1]





'''
    def determine(self, user_input):
        pos = self.pos_identifier(user_input)
        user_input = user_input.split(' ')
        try:
            if pos[0] == 'adv' and pos[1] == 'verb' and pos[2] == 'determ' and pos[3] == 'noun':    # information Requests
                pos.remove(pos[0])
                pos.remove(pos[1])
                user_input.remove(user_input[0])
                user_input.remove(user_input[1])
                if user_input[pos.index('noun')] == 'weather':
                    if 'forecast' in user_input:
                        resp = {'r_code': 'IR_W01'}
                        return resp
                    else:
                        resp = {'r_code': "IR_W00"}
                        return resp
                if user_input[pos.index('noun')] == 'definition':
                    if 'prep' in pos:
                        word = pos.index('prep')
                        word = user_input[word + 1]
                        resp = {'r_code': 'IR_D00', 'word': word}
                        return resp

        except IndexError:
            print("Index Error")
        try:
            if (pos[0] == 'verb' and pos[1] == 'noun') or (pos[2] == 'verb' and pos[3] == 'noun'): # action request
                if user_input[pos.index('verb')] == 'send':
                    if user_input[pos.index('noun')] == 'text':
                        resp = {'r_code': 'AR_S00'}
                        return resp
                elif user_input[pos.index('verb')] == 'initiate':
                    if user_input[pos.index('noun')] == 'learning':
                        resp = {'r_code': 'AR_SYSx0'}
                        return resp
                    if user_input[pos.index('noun')] == 'data':
                        resp = {'r_code': 'AR_SYSx1'}
                        return resp
                elif user_input[0] == 'set':
                    if 'reminder' in user_input:
                        user_input.remove('set'); user_input.remove('reminder')
                    if 'for' in user_input:
                        time = user_input[user_input.index('for') + 1]
                        user_input[user_input.index('for') + 1] = ''
                        user_input.remove('for')
                        resp = {'r_code': 'AR_R00', 'time': time, 'string': ' '.join(user_input)}
                    else:
                        print("develop")
                        resp = 'dev'
                    return resp

        except IndexError:
            user_input = ' '.join(user_input)
            return user_input

        try:
            print(user_input)
            print(pos)
            if pos[0] == 'adv' and pos[1] == 'aux_verb' and pos[2] == 'sub':
                if user_input[3] == 'have' and user_input[4] == 'to' and user_input[5] == 'do':
                    resp = {'r_code': "IR_R00"}
                    return resp
            elif pos[0] == 'verb' and pos[1] == 'obj':
                if user_input[3] == 'to':
                    user_input[0] = ''; user_input[1] = ''; user_input[3] = ''
                    for _, word in enumerate(user_input):
                        if word in self.time_periods:
                            time = word
                            user_input[_] = ''
                            break
                    resp = {'r_code': "AR_R00", 'time': time, }
        except IndexError:
            return user_input
'''




    # pos = ['adverb', 'verb', 'determiner', 'noun']
    # asking for information


'''
    if pos[0] == 'adverb' and pos[1] == 'verb':
        determ = pos.index('determiner')
        if pos[(determ + 1)] == 'noun':
            request = pos[(determ + 1)]
            return request
'''

'''
list of funtionality:
weather
    weather and forecast
usertracking
contact(sms)
dictionary
response

'''
