from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
import pickle
from sys import stdout as cout
import time

clf = None

data = [
    [[('I', 'PRP'), ('have', 'VBP'), ('to', 'TO'), ('go', 'VB')], 'AR'],
    [[('I', 'PRP'), ('will', 'MD'), ('have', 'VB'), ('to', 'TO'), ('go', 'VB')], 'AR'],
    [[('I', 'PRP'), ('need', 'VBP'), ('to', 'TO'), ('go', 'VB')], 'AR'],
    [[('Set', 'VB'), ('a', 'DT'), ('new', 'JJ'), ('reminder', 'NN')], 'AR'],
    [[('Set', 'VB'), ('a', 'DT'), ('reminder', 'NN')], 'AR'],
    [[('Set', 'VB'), ('reminder', 'NN')], 'AR'],
    [[('Send', 'VB'), ('a', 'DT'), ('text', 'NN')], 'AR'],
    [[('Send', 'VB'), ('text', 'NN')], 'AR'],
    [[('What', 'WP'), ('is', 'VBZ'), ('the', 'DT')], 'IR'],
    [[('What', 'WP'), ('do', 'VBP')], 'IR'],
    [[('what', 'WP'), ('is', 'VBZ'), ('on', 'IN')], 'IR'],
    [[('Where', 'WRB'), ('is', 'VBZ')], 'IR'],
    [[('Can', 'MD'), ('you', 'PRP'), ('tell', 'VB'), ('me', 'PRP')], 'IR'],
    [[('What', 'WP'), ('will', 'MD')], 'IR']
]

# intent = [('I', 'PRP'), ('have', 'VBP'), ('to', 'TO'), ('go', 'VB')]
def features(intent):
    """
    Tags 'Intent Chunk' with features for analysis by machine learning module. \n
    :param intent: Chunks['intent'] | Language Chunk showing intent.
    :type intent: list
    :return: A Feature tagged element.
    :rtype: dict
    """
    # Var Scope
    verb_tags = ['VB', 'VBZ', 'VBP']

    # String: convert tuple to string | ('I', 'PRP') >> I/PRP
    # Verb: Append any verbs in chunk | Tuple
    # Noun: Append any nouns in chunk | Tuple
    string = [tuple_to_string(tup) for tup in intent]
    verb = [tup for tup in intent if tup[1] in verb_tags]
    noun = [tup for tup in intent if tup[1] == 'NN']

    # Feature tag intent | If no verbs in Intent -> Return with |
    # 'before_verb' and 'after_verb' as 'NULL'                  |
    if len(verb) > 0:
        return {
            'intent': ' '.join(string),
            'first_word': string[0],
            'last_word': string[-1],
            'verb': '' if len(verb) == 0 else string[intent.index(verb[0])],
            'verb_location': '' if len(verb) == 0 else intent.index(verb[0]),
            'before_verb': '' if intent.index(verb[0]) == 0 else string[intent.index(verb[0]) - 1],
            'after_verb': '' if intent.index(verb[0]) == len(intent) - 1 else string[intent.index(verb[0]) + 1],
            'noun': string[intent.index(noun[0])] if len(noun) > 0 else ''
        }
    else:
        return {
            'intent': ' '.join(string),
            'first_word': string[0],
            'last_word': string[-1],
            'verb': '' if len(verb) == 0 else string[intent.index(verb[0])],
            'verb_location': '' if len(verb) == 0 else intent.index(verb[0]),
            'before_verb': 'NULL',
            'after_verb': 'NULL',
            'noun': string[intent.index(noun[0])] if len(noun) > 0 else ''
        }


def transform_to_dataset(sentences):
    """
    Transform list of sentences into feature tagged dataset
    for analysis by machine learning algorithm.\n
    Returns:
        * x - feature tagged sentence
        * y - action request type\n
    :param sentences: Sentences to be transformed to dataset
    """
    # Var Scope
    x, y = [], []

    for sent in sentences:
        x.append(features(sent[0]))
        y.append(sent[1])
    return x, y

def tuple_to_string(tup):
    """
    Convert a tuple to a string separated by a '/'\n
    :param tup: Tuple to be converted to String
    :return: String
    """
    return tup[0] + "/" + tup[1]

def analyse_intent(sentance):
    """
    Predict request type using Sklearn Machine Learning Algorithm.\n
    :param sentance: Intent Chunk to be analysed
    :return: Predicted Request Type
    """
    req_type = clf.predict([features(sentance)])
    return req_type

def trainData():
    """
    Train Machine Learning Algorithm. \n
    :return: cout Training complete Confirmation
    """
    x, y = transform_to_dataset(data)
    clf.fit(x[:10], y[:10])
    return cout.write('Classifier Training Complete...\n')

def dumpTraining():
    """ Dump CLF data to file. """
    with open('reqType.clf', 'wb') as f:
        pickle.dump(clf, f)
        f.close()
    return

def importTraining():
    """ Import CLF Data from dump file"""
    global clf
    with open('reqType.clf', 'rb') as f:
        clf = pickle.load(f)
    return

def init_clf():
    """ Initiate Machine Learning Algorithm """
    global clf
    clf = Pipeline([
        ('vectorizer', DictVectorizer(sparse=False)),
        ('classifier', DecisionTreeClassifier(criterion='entropy'))
    ])
    trainData()


##################################################################



"""
test_sent = [('I', 'PRP'), ('got', 'VBD'), ('to', 'TO'), ('go', 'VB')]

init_clf()
time.sleep(2)
test = analyse_intent(test_sent)
print(test)
"""

