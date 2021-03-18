from bin.inf.dictionary import WordHandle as WH

from bin.inf.weather import Weather
from bin.system.contact import Contact

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
        'reminders': ['remind', 'reminders', 'reminder', 'to do'],
        'sms': ['sms', 'message', 'text']
    }
    # Language Directives
    ACTION_REQ = ['i have']
    INFORMATION_REQ = ['what is', 'how is', 'who is', 'where is', 'when is']

    adverbs = ['what', 'how', 'why', 'to']
    verbs = ['is', 'send', 'initiate', 'set', 'remind', 'do', 'have']
    aux_verbs = ['do', 'have']
    nouns = ['weather', 'text', 'forecast', 'definition', 'learning', 'data']
    determiner = ['the', 'a', 'an']
    time_periods = ['today', 'tomorrow', 'afternoon', 'tonight', 'night', 'evening', 'morning']
    preposition = ['of', 'for']
    obj_pronoun = ['me']
    sub_pronoun = ['I']

    def __init__(self):
        self.pos = []
        self.userInput = 'what is the weather forecast for tomorrow'
        self.reqType = ''

    def determine(self, user_input):
        print(user_input)
        self.formatForDetermine(user_input)
        code = ''
        if self.reqType == "IR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['weather']: # Weather Feature
                    output = self.determineWeatherReq()
                    code = output['code']
                    code = self.reqType + code
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
                    code = self.reqType + code
                    resp = {'r_code': code, 'word': output['word']}
                    return resp
                elif word in self.FEATURE['reminders']:
                    output = self.determineReminderReq()
                    code = output['code']
                    code = self.reqType + code
                    resp = {'r_code': code, 'time': output['time']}
                    return resp
        elif self.reqType == "AR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['sms']:
                    output = self.determineSmsReq()
                    code = output['code']; code = self.reqType + code
                    if code == 'AR_S01':
                        return {'r_code': code, 'recip': output['recip']}
                    else:
                        return {'r_code': code}

    def formatForDetermine(self, userInput):
        self.userInput = userInput
        self.pos = self.pos_identifier(user_input=self.userInput)
        self.reqType = self.determineReqType()

    def determineReqType(self):
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        for _ in self.INFORMATION_REQ:
            if _ in self.userInput:
                return "IR"
        if self.pos[0] == 'adv' and self.pos[1] == 'verb':
            if dataSplit[0] =='what' or dataSplit[0] == 'how':
                return "IR"
        for _ in self.ACTION_REQ:
            if _ in self.userInput:
                return "AR"
        for _ in self.verbs:
            if _ in self.userInput:
                return "AR"

    def determineSmsReq(self):
        if 'to' in self.userInput:
            dataSplit = SpeechRecognition.langSplit(self.userInput)
            recip = dataSplit[dataSplit.index('to') + 1]
            output = {'code': "_S01", 'recip': recip}
            return output
        else:
            return {'code': "_S00"}

    def determineWeatherReq(self):
        # what is the weather forecast for tomorrow
        time = None
        for word in self.time_periods:
            if word in self.userInput:
                time = word
        if time:
            return {'code': '_W01', 'time': time}
        elif time is None:
            return {'code': '_W00'}

    def determineDictReq(self):
        # what is the definition of ****
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        wordIndex = self.pos.index('prep') + 1
        if dataSplit[wordIndex - 2] == 'definition':
            word = dataSplit[wordIndex]
            return {'code': '_D00', 'word': word}
        else:
            print('error')
            return

    def determineReminderReq(self):
        #what do i have to do today
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        for word in dataSplit:
            if word in self.time_periods:
                time = word
                resp = {'code': '_R00', 'time': time}
                return resp





    @staticmethod
    def langSplit(data):
        data = data.split(' ')
        dataSplit = []
        for i, word in enumerate(data):
            if word == 'to' and data[i + 1] == 'do':
                dataSplit.append('to do')
            else:
                dataSplit.append(word)
        return dataSplit

    def pos_identifier(self, user_input):
        pos = []
        word_list = SpeechRecognition.langSplit(user_input)
        for word in word_list:
            if word in self.adverbs:
                pos.append("adv")
            elif word in self.verbs:
                pos.append("verb")
            elif word in self.aux_verbs:
                pos.append("aux_verb")
            elif word in self.nouns:
                pos.append("noun")
            elif word in self.determiner:
                pos.append("determ")
            elif word in self.preposition:
                pos.append('prep')
            elif word in self.sub_pronoun:
                pos.append('sub')
            elif word in self.obj_pronoun:
                pos.append('obj')
        return pos;

    def smsHandler(self, packet):
        packet.split('::')
        recip = packet[1]
        packet





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
