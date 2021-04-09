import threading
###############################################################
# Time Handler
from sys import stdout as cout
from time import process_time
from datetime import datetime, timedelta
from bin.system.timeHandler import TimeHandler
from nltk import RegexpParser, ne_chunk, Tree
from nltk import word_tokenize, pos_tag, WordNetLemmatizer
from nltk import CoreNLPParser
#########################################################################################

class LanguageProcessing:
    LEMM = WordNetLemmatizer()
    TH = TimeHandler()
    G_CASE_TIME = r"""
        NP: {<IN|DT><CD>+<N.*>}
            {<NNP>?<IN><CD>+}
            {<NNP><DT>?<CD>}
            {<IN>?<N.*|DT>+<CD>}
            {<NP><IN><CD>}
    """
    G_CASE_INTENT = r"""
        VP: {^<PRP><MD>?<VB.*><TO>}
            {^<PRP><MD|VB.*>}
            {^<VB.*|DT>+<JJ>?<NN>}
            {^<PRP><VB.*><PRP\$|DT>*}
    """
    G_CASE_SUBJECT = r"""      # set a? new? reminder to go to the bank <time>   ???{^<NNS>?<VBP>+<TO>?}???
        NP: {<PRP\$>?<DT|JJ|N.*>+}          # Chunk sequences of DT, JJ, NN
        PP: {<IN|TO><NP>}               # Chunk prepositions followed by NP
        VP: {<VB.*>+<TO>?<NP|PP|CLAUSE>+} # Chunk verbs and their arguments
        CLAUSE: {<NP><VP>}           # Chunk NP, VP
    """
    G_CASE_CONDITIONAL = r"""
    """
    PERIOD_REF = [
        'right now', 'later', 'today',
        'tonight', 'tomorrow', 'week',
        'month', 'year', 'morning',
        'afternoon', 'evening', 'night'
    ]

    def __init__(self):
        self.stringQ = []
        self.ParserSubject = RegexpParser(self.G_CASE_SUBJECT)
        self.ParserTime = RegexpParser(self.G_CASE_TIME, loop=2)
        self.ParserIntent = RegexpParser(self.G_CASE_INTENT)
        self.coreNLP = self.coreNLPinit()

    def coreNLPinit(self):
        try:
            self.parser = CoreNLPParser(url='http://localhost:9000', tagtype='pos')
            return True
        except:
            return False

    def processSent(self, string):
        # Var Decleration
        self.string = None; self.tokens = None; self.time_chunk = None
        self.pos_tagged = None; self.namedEntitys = None
        self.phrases = {'time_chunk': []}

        self.string = string # self.LEMM.lemmatize(string)
        if not self.coreNLP:
            self.tokens = word_tokenize(self.string)
            #self.pos_tagged = ut.tag(self.tokens)
            self.pos_tagged = pos_tag(self.tokens)
            self.namedEntitys = [elem for elem in ne_chunk(self.pos_tagged) if type(elem) == Tree]
        elif self.coreNLP:
            self.tokenObj = self.parser.tokenize(self.string); self.tokens = list(self.tokenObj)
            self.pos_tagged = self.parser.tag(self.tokens)
        self.chunkSent()
        #self.timeChunkAnalysis()
        return self.phrases

    def chunkSent(self):
        #   Discover Time Chunk
        chunk = self.ParserTime.parse(self.pos_tagged)   # tag time chunk
        for i, subtree in enumerate(chunk):   #
            if type(subtree) == Tree:
                self.phrases['time_chunk'].append((i, chunk[i]))
                chunk[i] = 'NULL'
        for x in range(chunk.count('NULL')): chunk.remove('NULL')
        chunk = self.ParserIntent.parse(chunk)
        for i, subtree in enumerate(chunk):
            if type(subtree) == Tree:
                self.phrases['intent'] = (i, chunk.pop(i))
        chunk = self.ParserSubject.parse(chunk)
        for i, subtree in enumerate(chunk):
            if type(subtree) == Tree:
                self.phrases['S:{}'.format(i)] = (i, chunk.pop(i))
        return True
    """
    def timeChunkAnalysis(self):
        try:
            chunk = self.phrases['time_chunk']; chunk = chunk[0]
        except KeyError:
            for phrase in self.phrases:
                if 'S:' in phrase:
                    chunk = self.phrases[phrase]

        tags = [token for token in chunk[1]]
        try:
            tags.remove(['IN' for token in tags])
        except ValueError:
            print('ValueError in IN removal')

        digets = [token for token in tags if 'CD' in token]
        # Parse/Anal. Topography(AM/PM)
        topograpgy = [tags.pop(x) for x in tags if 'am' in x or 'pm' in x]
        # Parse/Anal. Date(March 3rd | 3/12)

        # analyse digits
        time = [digets if digets.count(':') > 0 and digets.count(type(int)) in [1, 3, 4] else None]
        """
    @staticmethod
    def untag(tagged_sentence):
        return [w for w, t in tagged_sentence]

    @staticmethod
    def phrase2string(phrase):
        string = [" ".join([token for token, pos in phrase.leaves()])]
        return " ".join(string)

###############################################################################################
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
sent0 = "I have class tomorrow at 5:30"
sent1 = "I have to go take my test tomorrow at 5"
sent2 = "I will have my lecture at 2"
sent3 = "Set a new reminder to go to the grocery store tomorrow at 2"
sent4 = "Set a reminder to take the kids to soccer at 1"
sent5 = "Set reminder for March 3rd to order bones"
sent6 = "I need to finish my homework on March 3rd by 2:30"
sentA0 = "I am going to the beach on the 3rd"
sentA1 = "What is the definition of angry"
sentList = ["I have class tomorrow at 5:30", "I have to go take my test Tuesday at 5", "I will have my lecture at 2", "Set a new reminder to go to the grocery store tomorrow at 2",
            "Set a reminder to take the kids to soccer at 1", "Set reminder for March 3rd to order bones", "I need to finish my homework on March 3rd by 2:30", "I am going to the beach on the 3rd",
            "What is the definition of angry"]
text = 'Set a reminder to take the kids to soccer at 2:30. i have to go to the grocery store at 3.'
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
LP = LanguageProcessing()
#>> Class 'LanguageProcessesing' run loop

st = process_time()
for sent in sentList:
    cout.write(str(LP.processSent(sent)))
    cout.write('\n')


print("--- %.2f seconds" % (process_time() - st))


