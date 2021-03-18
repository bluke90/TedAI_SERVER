from os import listdir
import requests
import json
from sys import stdout as std
from lxml.etree import ElementTree as ET

#url = "https://rapidapi.p.rapidapi.com/words/incredible/definitions"

headers = {
    'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
    'x-rapidapi-key': "0e9ec5131amshcda7cbcbe0a75fdp19a768jsna57942425cf0"
    }

#response = requests.request("GET", url, headers=headers)
#print(response.text)



class Dictionary:

    def __init__(self):
        self.dictionary = {}
        std.write("#D>> Indexing Dictionary Data Files...\n")
        self.dir_list = [f for f in listdir('./data/dictionaries')]
        self.propositions = []
        std.write("#D>> Stacking Dictionaries To Memory...\n")
        self.load_dictionary()
        self.skip_index = []
        self.handler = WordHandle()

    def load_dictionary(self):
        for dictionary in self.dir_list:
            dict_path = './data/dictionaries/{}'.format(dictionary)
            if dictionary == 'propositions.px1':
                with open(dict_path, 'r') as file:
                    data = file.read()
                    file.close()
                data = data.split('\n')
                for line in data:
                    if line != '':
                        self.propositions.append(line)

            else:
                with open(dict_path, 'r') as file:
                    data = file.read()
                    file.close()
                data = data.split('\n')
                for line in data:
                    if line != '' and line != ' ':
                        split_line = line.split(' = ')
                        self.dictionary[split_line[0]] = split_line[1]
        return

    def store_def(self, word, definition):
        std.write("#D>> Storing newly learned definition...")
        self.dictionary[word] = definition
        while True:
            for dictionary in self.dir_list:
                dictionary_name = './data/dictionaries/{}'.format(dictionary)
                try:
                    '''
                    data = {}
                    data[word] = []
                    data[word].append({
                        'definition': definition,
                        'pos': pos
                    })
                    '''
                    with open(dictionary_name, 'a') as f:
                        f.write('{} = {}\n'.format(word, definition))
                        f.close()
                        return True
                except UnicodeEncodeError:
                    f.close()
                return True

    def create_data_file(self):
        dict_name = 'dictionary_{}'.format((len(self.dir_list) + 2))
        open(dict_name, 'w')
        self.dir_list = [f for f in listdir('./data/dictionaries')]

    def search_word(self, word):
        if word not in self.dictionary and word not in self.skip_index:
            url = 'https://rapidapi.p.rapidapi.com/words/{}'.format(word)
            req = requests.request("GET", url, headers=headers)
            try:
                data_raw = req.json()
            except json.decoder.JSONDecodeError:
                return 'Unable to pull definition.'
            try:
                new_def = data_raw['results'][0]['definition']
                print(
                    "What does {} mean?\n".format(word),
                    "Word: {} | Defanition: {}".format(word, new_def)
                )

            except KeyError:
                # msg = Contact("What does {} mean?".format(word))
                # new_def = Contact.send_recv(msg)
                # Ask user via speech
                # ask via prompt
                new_def = 'skip'  # input("What does {} mean?".format(word))
                # if skip continue to next word without storing defanition
                if new_def == 'skip':
                    self.skip_index.append(word)
                    return
                print("Word: {} | Defanition: {}".format(word, new_def))
            except IndexError:
                print(word)
                return

            if new_def:
                self.store_def(word, new_def)
                return 'The definition of {} is {}'.format(word, new_def)


        elif word in self.dictionary:
            return 'The definition of {} is {}'.format(word, self.dictionary[word])

        elif word in self.skip_index:
            return 'Unkown word'

        else:
            # print('out of words')
            return

    def proposition_removal(self, body):

        key_words = self.propositions
        body = body.split(' ')
        for word in key_words:
            if word in body:
                body.remove(word)
        body = ' '.join(body)
        return body


class Learning:
    punctuation = ['.', ',', ';', ':', '!', '(', ')', '{', '}', '[', ']', '"', "'"]

    def __init__(self, dictionary):
        self.dictionary_class = dictionary
        self.dictionary = self.dictionary_class.dictionary
        self.handler = WordHandle()

    def learning(self):
        while True:
            # for object in dir
            for n in list(self.dictionary):
                # if word not nothing
                if n != " " or word != "":
                    # set defanition == defanition of n
                    defanition = self.dictionary[n]
                    # split the defanition into list
                    defanition = defanition.split(' ')
                    # for each word in the defition
                    for word in defanition:

                        word = self.handler.punctuation_removal(word)
                        # check if word is known and make sure it hasnt already been skipped
                        if word not in self.dictionary_class.skip_index and word not in self.dictionary:
                            new_def = self.dictionary_class.search_word(word)
                elif word == " " or word == "":
                    print("I belive i may be out of new words.")

    def learn_word_handling(self, word):
        word = word.lower()
        split_word = list(word)
        for letter in split_word:
            if letter in self.punctuation:
                split_word.remove(letter)

        word = ''.join(split_word)
        return word


class WordHandle:

    def __init__(self):
        self.operators = []
        self.load_data()

    def load_data(self):
        with open('./data/operators/operators.px1', 'r') as file:
            data = file.read()
            file.close()
        data = data.split('\n')
        punctuation = data.index('<Punctuation>')
        math = data.index('<Math>')
        for n in data:
            if n != '<Punctuation>':
                self.operators.append(n)
            if n == '<Math>':
                break

    def punctuation_removal(self, string):
        string = list(string)
        for x in self.operators:
            while x in string:
                string.remove(x)

        string = ''.join(string)
        return string

    def contraction_process(self, string):
        data = string.split(' ')
        string = []
        for word in data:
            word = list(word)
            if "\'" in word:
                for i, letter in enumerate(word):
                    if letter == "\'":
                        if word[i+1] == 's':
                            word[i] = ' '
                            word[i+1] = 'is'
                            string.append(''.join(word))
                            continue
            elif '\'' not in word:
                string.append(''.join(word))
        return ' '.join(string)


