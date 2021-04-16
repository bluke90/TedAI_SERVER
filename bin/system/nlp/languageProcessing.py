import time
import threading
import queue
from random import randint
from sys import stdout as cout
from bin.system.nlp.determineReqType import analyse_intent, init_clf
from bin.system.timeHandler import TimeHandler
from nltk import RegexpParser, ne_chunk, Tree
from nltk import word_tokenize, pos_tag, WordNetLemmatizer
from nltk import CoreNLPParser
from itertools import permutations
#########################################################################################


class LanguageProcessing:
    LEMM = WordNetLemmatizer()
    TH = TimeHandler()
    G_CASE_TIME = r"""
        NP: {<IN|DT>+<PERIOD>}
            {<PERIOD|NNP>+<IN><CD>}
            {<PERIOD><PERIOD>}
    CLAUSE: {<NP><IN><CD>}
            {<IN><CD><NP>}
    """
    G_CASE_INTENT = r"""
        VP: {^<WP><VBZ>}
            {^<PRP><MD>?<VB.*><TO>?}
            {^<VB.*|DT>+<JJ>?<NN>}
            {^<PRP><VB.*><PRP\$|DT>*}
            {^<PRP><VBD><TO>}
    """
    G_CASE_SUBJECT = r"""      # set a? new? reminder to go to the bank <time>   ???{^<NNS>?<VBP>+<TO>?}???
        NP: {<PRP\$>?<DT|JJ|N.*>+}          # Chunk sequences of DT, JJ, NN
        PP: {<IN|TO><NP>}               # Chunk prepositions followed by NP
        VP: {<VB.*>+<TO>?<NP|PP|CLAUSE>+} # Chunk verbs and their arguments
        CLAUSE: {<NP><VP|PP>}           # Chunk NP, VP
    """
    G_CASE_CONDITIONAL = r"""
    """
    PERIOD_REF = [
        'right now', 'later', 'today',
        'tonight', 'tomorrow', 'week',
        'month', 'year', 'morning',
        'afternoon', 'evening', 'night'
    ]

    def __init__(self, **kwargs):
        self.ThreadLimit = kwargs['threads']
        self.stringQ = queue.Queue()
        self.complete = {}
        self.ParserSubject = RegexpParser(self.G_CASE_SUBJECT)
        self.ParserTime = RegexpParser(self.G_CASE_TIME)
        self.ParserIntent = RegexpParser(self.G_CASE_INTENT)
        self.coreNLP = self.core_nlp_init()
        self.wrkrList = []
        self.thread_initialization()

    #>>> Thread handler
    def thread_initialization(self):
        for i in range(4):
            wrkr = threading.Thread(target=self.worker, daemon=True)
            wrkr.start()
        return True

    def queProcessing(self, string):
        ref_id = randint(100, 999)
        string = [ref_id, string]
        self.stringQ.put(string)
        self.complete[ref_id] = None
        return ref_id

    def worker(self):
        wrkr_id = len(self.wrkrList) + 1    # Create Worker Thread Reference ID
        cout.write('Worker Thread #{}: Initialization Successful...\n'.format(wrkr_id))
        self.wrkrList.append(wrkr_id)
        while True:
            req = self.stringQ.get()
            ref_id = req[0]; string = req[1]
            cout.write('Worker {} processing request {}\n'.format(wrkr_id, str(ref_id)))
            tokenized_sentance, tagged_sentance = self.process_with_core(string) if self.coreNLP == True else self.process_with_standard(string)
            tagged_sentance = self.parse_period_ref(tagged_sentance)
            chunks = self.chunkSent(tagged_sentance)
            self.complete[ref_id] = chunks
            cout.write('Worker {} completed request {}\n'.format(wrkr_id, str(ref_id)))
            self.stringQ.task_done()

    def completeQ(self, **kwargs):
        if kwargs.get('ref_id') is not None:
            if type(kwargs['ref_id']) is str or type(kwargs['ref_id']) is int:
                while self.complete[kwargs['ref_id']] is None: continue
                output = self.complete.pop(kwargs['ref_id'])
                return output
            elif type(kwargs['ref_id']) is list:
                output = []
                while True:
                    for elem_id in kwargs['ref_id']:
                        completed_elem = self.complete.get(elem_id)
                        if completed_elem is not None:
                            output.append(completed_elem)
                            self.complete.pop(ref_id)
                        elif len(kwargs['ref_if']) == 0:
                            return output

        elif kwargs.get('all') is True:
            self.stringQ.join()
            output = []
            for elem in list(self.complete):
                output.append(self.complete.pop(elem))
            return output

    ###############################

    def core_nlp_init(self):
        try:
            self.parser = CoreNLPParser(url='http://localhost:9000', tagtype='pos')
            return True
        except:
            cout.write("!CoreNLP Failure!\n")
            return False

    # Process string for language processing
    def process_sent(self, string):
        """Processes the sentence using CoreNLPParser,
        returning a list of tokenized words and
        a list of tokens tagged with their corresponding Part of Speech Tags\n
        :param string: the string to be processed
        :returns: tokenized_string, tagged_string"""
        if not self.coreNLP:    # Check if CoreNLP Server is Available
            self.process_with_standard(string)
        elif self.coreNLP:  # Use CoreNLP if Available
            tokenized_string, tagged_string = self.process_with_core(string)
        else:
            raise Exception("Error in Processing sentence")
        return tokens, pos_tagged

    # Process using CoreNLPParser
    def process_with_core(self, string):
        """Process the sentence using CoreNLPParser,
        returning a list of tokenized words and
        a list of tokens tagged with their corresponding Part of Speech Tags\n
        :param string: the string to be processed
        :returns: tokenized_string, tagged_string"""
        tokenized_string = list(self.parser.tokenize(string))
        tagged_string = list(self.parser.tag(tokenized_string))


    # Process using nltk standard parser
    def process_with_standard(self, string):
        """Process the sentence using NLTK Standard Parser,
        returning a list of tokenized words and
        a list of tokens tagged with their corresponding Part of Speech Tags\n
        :param string: the string to be processed
        :returns: tokenized_string, tagged_string"""
        tokenized_string = word_tokenize(string)
        tagged_string = pos_tag(tokenized_string)

    # Handle Sentace Chunking
    def chunkSent(self, pos_tagged):
        phrases = {'time_chunk': [], 'subject': [], 'intent': []}
        #   Discover Time Chunk
        chunk = self.ParserTime.parse(pos_tagged)   # tag time chunk
        for i, subtree in enumerate(chunk):   #
            if type(subtree) == Tree:
                phrases['time_chunk'].append(chunk.pop(i))
        if len(phrases['time_chunk']) == 0: phrases['time_chunk'] = None
        chunk = self.ParserIntent.parse(chunk)
        for i, subtree in enumerate(chunk):
            if type(subtree) == Tree:
                phrases['intent'].append(chunk.pop(i))
        chunk = self.ParserSubject.parse(chunk)
        if type(chunk) == Tree:
            phrases['subject'].append(chunk)
        else:
            for i, subtree in enumerate(chunk):
                if type(subtree) == Tree:
                    phrases['subject'].append(chunk.pop(i))
        return phrases

    @staticmethod
    def untag(tagged_sentence):
        return [w for w, t in tagged_sentence]

    @staticmethod
    def phrase2string(phrase):
        string = [" ".join([token for token, pos in phrase.leaves()])]
        return " ".join(string)

    @staticmethod
    def parse_period_ref(tagged):
        period_ref = [
            'right now', 'later', 'today',
            'tonight', 'tomorrow', 'week',
            'month', 'year', 'morning',
            'afternoon', 'evening', 'night'
        ]
        for i, tup in enumerate(tagged):
            if tup[0] in period_ref:
                new = (tup[0], 'PERIOD')
                tagged[i] = new
        return tagged

    @staticmethod
    def convert_time_chunk(time_chunk):     # (CLAUSE at/IN 5/CD (NP in/IN the/DT morning/PERIOD))
        """
        Convert time chunk to Date/Time.
        :param time_chunk: Chunk from input containing date/time information
        :return:
        """
        # Var Scope
        priority_tags = ['NNP', 'PERIOD', 'CD']
        feature_tagged, _time, _date, _day = [], [], [], []

        # remove determiner words from chunk
        for token, pos in list(time_chunk):
            if pos == 'DT':
                time_chunk.remove((token, pos))

        # Get features for words if its a
        # Proper Noun('March'), Period('tomorrow'), or digit('5:30)
        _index = 0
        for token, pos in list(time_chunk):
            if pos in priority_tags:
                feature_tagged.append(LanguageProcessing.time_chunk_features(time_chunk, (token, pos), new_index=_index))
                _index += 1
                continue

        # Assess feature tagged tokens for time and date information
        '''MM:DD:YY HH:MM | PERIOD{Tuesday = DD, Morning = TT} DIGIT|CD{5:30 = TT, 5th = DD} NNP{March = DD, Tuesday = DD}'''
        period_perm = permutations(['CD', 'IN'])
        for i, elem in enumerate(feature_tagged):
            if elem['pos'] == 'NNP':
                if elem['next_elem_1'] == 'NNP':
                    feature_tagged, elem = LanguageProcessing.merge_features(feature_tagged[i], feature_tagged[i+1], feature_tagged)

                if elem['next_elem_1'] == 'CD' and (elem['next_elem_1']):


                _time.append(LanguageProcessing.digit_check(elem, next_elem=False))





        for i, elem in enumerate(feature_tagged):
            if elem['pos'] == 'PERIOD':
                if elem['next_elem_1'][1] == 'PERIOD':  # Check for PERIOD::PERIOD
                    feature_tagged, elem = LanguageProcessing.merge_features(feature_tagged[i], feature_tagged[i+1], feature_tagged)

                if [elem['next_elem_1'][1], elem['next_elem_2'][1]] in period_perm:
                    _time.append([x[0] for x in [elem['next_elem_1'], elem['next_elem_2']] if x[1] == 'CD'])
                elif [elem['prev_elem_2'][1], elem['prev_elem_1'][1]] in period_perm:
                    _time.append([x[0] for x in [elem['prev_elem_2'], elem['prev_elem_2']] if x[1] == 'CD'])


    @staticmethod
    def digit_check(elem, **kwargs):
        """
        Check for permutation of a digit{CD} and a preposition{IN}
        Keyword:
            * next_elem: if False will not check next elements
            * prev_elem: if False will not check prev elements
        :param elem: Feature tagged element
        :return:
        """
        period_perm, _time = permutations(['CD', 'IN']), []     # All combinations of CD and IN
        if [elem['next_elem_1'][1], elem['next_elem_2'][1]] in period_perm and kwargs['next_elem'] is not False:
            _time.append([x[0] for x in [elem['next_elem_1'], elem['next_elem_2']] if x[1] == 'CD'])
        if [elem['prev_elem_2'][1], elem['prev_elem_1'][1]] in period_perm and kwargs['prev_elem'] is not False:
            _time.append([x[0] for x in [elem['prev_elem_2'], elem['prev_elem_2']] if x[1] == 'CD'])
        return _time


        # (CLAUSE 5/CD (NP morning/PERIOD))

    @staticmethod
    def time_chunk_features(time_chunk, token, **kwargs):
        """
        Adds features to token for analysis by machine learning module. \n
        Returns: <Dictionary>
            * 'word': word | 'pos': part of speech | 'index': token index
            * 'prev_elem_1': element + 1 | 'prev_elem_2': element + 2
            * 'next_elem_1': element - 1 | 'next_elem_2': element - 2
            * 'is_digit': True > if digit
            * 'token_digit': True > if digit after token | 'digit_token': True > if digit before token\n
        :param time_chunk: time_chunk from NLP Chunking
        :type time_chunk: list
        :param token: specified token in time_chunk for feature tagging
        :type token: tuple
        :keyword new_index: *OPTIONAL* overwrite index
        """
        index = time_chunk.index(token)
        return {
            'word': time_chunk[index][0],
            'pos': time_chunk[index][1],
            'index': kwargs['new_index'] if kwargs.get('new_index') is not None else index,
            'prev_elem_1': '' if index == 0 else time_chunk[index - 1],
            'prev_elem_2': '' if index < 2 else time_chunk[index - 2],
            'next_elem_1': '' if index == len(time_chunk) - 1 else time_chunk[index + 1],
            'next_elem_2': '' if index > len(time_chunk) - 2 else time_chunk[index + 2],
            'is_digit': True if type(time_chunk[index][0].isdigit()) else False,
            'token_digit': True if index != len(time_chunk) - 1 and time_chunk[index + 1][1] == 'CD' else False,
            'digit_token': True if index != 0 and time_chunk[index - 1][1] == 'CD' else False
        }

    @staticmethod
    def merge_features(elem_1, elem_2, time_chunk):
        """ Combines the features of elem_1 and elem_2, returns the time_chunk
        with elem_1 and elem_2 replaced with merged element. \n
        :param elem_1: Token 1, left token
        :type elem_1: dict
        :param elem_2: Token 2, right token
        :type elem_2: dict
        :param time_chunk: Feature tagged time Chunk to merge tokens
        :type time_chunk: list
        :returns: *list* Time Chunk with elements merged
        """
        # Create new element with the merged tokens |
        elem_x = {
            'word': '{} {}'.format(elem_1[0], elem_2[0]),
            'pos': elem_1[1],
            'index': elem_1['index'],
            'prev_elem_1': elem_1['prev_elem_1'],
            'prev_elem_2': elem_1['prev_elem_2'],
            'next_elem_1': elem_2['next_elem_1'],
            'next_elem_2': elem_2['next_elem_2'],
            'is_digit': True if type(elem_1[0]).isdigit() else False,
            'token_digit': elem_2['token_digit'],
            'digit_token': elem_1['digit_token']
        }
        # Replace element 1 with merged element(elem_x). |
        # Remove elem_2.                                 |
        time_chunk[elem_x['index']] = elem_x
        time_chunk.pop(elem_2['index'])

        # Subtract 1 from all index's after merged token. |
        for elem in range(elem_x['index'], len(time_chunk)):
            time_chunk[elem['index']] = time_chunk[elem['index']] - 1
        return time_chunk, elem_x

#########################################
init_clf()
defReq = 'I got to get up at 5 in the morning'
LP = LanguageProcessing(threads=4)
ST = time.process_time()
ref_id = LP.queProcessing(defReq)
chunks = LP.completeQ(ref_id=ref_id)
time_chunk = None if chunks['time_chunk'] == None else chunks['time_chunk'][0]  # list of trees
intent = (chunks['intent'][0])  # list of trees
subject = (chunks['subject'][0])  # list of trees

time_chunk = LP.convert_time_chunk(time_chunk.leaves())
reqType = analyse_intent(intent)
print("--- %.2f seconds" % (time.process_time() - ST))
print(chunks)
print(time_chunk)
print(intent)
print(subject)
print(reqType)