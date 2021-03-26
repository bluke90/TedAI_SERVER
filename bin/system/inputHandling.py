from bin.inf.dictionary import WordHandle as WH
from bin.system.connection import SQLConnection
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
    # Language Directives
    ACTION_REQ = ['i have']
    INFORMATION_REQ = ['what is', 'how is', 'who is', 'where is', 'when is']
    # Language
    adverbs = ['what', 'how', 'why', 'to']
    verbs = ['is', 'send', 'initiate', 'set', 'remind', 'do', 'have']
    aux_verbs = ['do', 'have']
    nouns = ['weather', 'text', 'forecast', 'definition', 'learning', 'data']
    determiner = ['the', 'a', 'an']
    time_periods = ['today', 'tomorrow', 'afternoon', 'tonight', 'night', 'evening', 'morning']
    preposition = ['of', 'for', 'at', 'on']
    obj_pronoun = ['me']
    sub_pronoun = ['I']
    # Natural Language Processing
    lemmatizer = WordNetLemmatizer()

    def __init__(self):
        self.SQL = SQLConnection()  # !
        # Array Init
        self.UIpos = []; self.userInput = ''; self.UIreqType = ''; self.like_req = {}
        # Get Data From Database : Stack Data to Dict.
        self.rawData = self.SQL.execSQL("SELECT * FROM lang_learning.like_req", fetch=1)
        for row in self.rawData: phrases = row[1].split(','); self.like_req[row[2]] = phrases

    def determine(self, user_input):
        print(user_input)
        self.formatForDetermine(user_input)
        if self.UIreqType == "IR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['weather']: # Weather Feature
                    output = self.determineWeatherReq()
                    code = output['code']
                    code = self.UIreqType + code
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
                    code = self.UIreqType + code
                    resp = {'r_code': code, 'word': output['word']}
                    return resp
                elif word in self.FEATURE['remind']:
                    output = self.determineReminderReq()
                    code = output['code']
                    code = self.UIreqType + code
                    resp = {'r_code': code, 'time': output['time']}
                    return resp
        elif self.UIreqType == "AR":
            for word in SpeechRecognition.langSplit(self.userInput):
                if word in self.FEATURE['sms']:
                    output = self.determineSmsReq()
                    code = output['code']; code = self.UIreqType + code
                    if code == 'AR_S01':
                        return {'r_code': code, 'recip': output['recip']}
                    else:
                        return {'r_code': code}
                if word in self.FEATURE['remind']:
                    output = self.determineReminderAct()

    def formatForDetermine(self, userInput):
        self.userInput = userInput
        self.UItokens = word_tokenize()
        self.UIpos = pos_tag(self.UItokens)
        self.userInput = self.lemmatizer.lemmatize(self.userInput)
        #self.pos = self.pos_identifier(user_input=self.userInput)
        self.UIreqType = self.determineReqType()

    def determineReqType(self):
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        for _ in self.INFORMATION_REQ:
            if _ in self.userInput:
                return "IR"
        if self.UIpos[0] == 'adv' and self.UIpos[1] == 'verb':
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
        wordIndex = self.UIpos.index('prep') + 1
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

    def determineReminderAct(self):
        dataSplit = SpeechRecognition.langSplit(self.userInput)
        cursor = 0; subject = []; time_elements = []
        vLoc = self.UIpos.index('verb')
        # check for time | Chunk = NP: {<NN>+<IN>?<CD>}
        for i, word in enumerate(dataSplit):
            if word in self.time_periods:
                time_elements.append(word); dataSplit.pop(i)
                if dataSplit[i-1] in self.preposition: dataSplit.pop(i-1)
            if ':' in word: time_elements.append(word); dataSplit.pop(i)
            if word.isdigit() and dataSplit[i-1] in self.preposition:
                time_elements.append(word); dataSplit.pop(i); dataSplit.pop(i-1)
        # if reminder in sentance check for adjective
        if 'reminder' in dataSplit:
            cur = dataSplit.index('reminder') - 1
            if self.UIpos[cur] == 'adj': dataSplit.pop(cur)
            if self.UIpos[cur - 1] == 'determ': dataSplit.pop(cur - 1)
        # discover subject
        if vLoc > 0:
            for word in range(0, (vLoc)):
                dataSplit.pop(cursor)
                cursor += 1
        if dataSplit[cursor] == 'reminder':
            dataSplit.pop(cursor)
            cursor += 1
        if dataSplit[cursor] in self.determiner:
            dataSplit.pop(cursor)
            cursor += 1
        """
        'Set reminder for tomorrow'
        grammar = r'''
            VP: {<VB.*>+<DT>?<JJ>?<NN>+<TO|IN>?}
            NP: {<VB|NN><.*>.}
            {<NN><IN>?<CD>}
            '''
        ne_chunk()
        """


# convert word to datetime



    def phraseMatch(self, string):
        for i, word in enumerate(string):
            if self.isPrep(word):
                string[i] = 'prep'
        elements = []
        for phrase in self.like_req:
            phrase = phrase.split(' ')
            wordCount = 0; removalCount = 0
            for i, word in enumerate(string):
                if word == 'prep':
                    elements.append(string[i + 1])

                if word == phrase[wordCount]:
                    wordCount += 1; removalCount +=1




    def isPrep(self, word):
        if word in self.preposition:
            return True
        else:
            return False




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
