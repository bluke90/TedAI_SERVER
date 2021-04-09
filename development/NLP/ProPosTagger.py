# Blake Ganzerla

###############> IMPORTS <###############
from sys import stdout as cout
from nltk.corpus import treebank, twitter_samples
from nltk.corpus.reader import TaggedCorpusReader
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
# ....................
# download('treebank')

##########> Global Variable Declarations <##########
training_data = treebank.tagged_sents()
clf = Pipeline([
    ('vectorizer', DictVectorizer(sparse=False)),
    ('classifier', DecisionTreeClassifier(criterion='entropy'))
])


def features(sentence, index):
    """ sentence: [w1, w2, ...], index: the index of the word """
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'is_capitalized': sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }



def trasnform_to_dataset(tagged_sents):
    # Array Declaration
    x, y = [], []
    cout.write(tagged_sents)
    for tagged in tagged_sents:
        for index in range(len(tagged)):
            x.append(features(untag(tagged), index))
            y.append(tagged[index][1])

    cout.write('x = {} | y = {}'.format(x, y))
    return x, y


def untag(tagged_sentence):
    return [w for w, t in tagged_sentence]

def pos_tag_learn(sentance):
    tags = clf.predict([features(sentance, index) for index in range(len(sentance))])
    return zip(sentance, tags)


#>>>> Training with new corpus
path = 'Data/'
reader = TaggedCorpusReader(path, '.*')
training_set = reader.tagged_sents()
#print(reader.words('ca0.txt'))
#print(reader.tagged_sents('ca0.txt'))

###############> Training Example With Treebank <###############
#cutoff = int(.75 * len(training_data))
#training_set = training_data[:cutoff]
#test_set = training_data[cutoff:]
#print(training_set)
#print(len(training_set))
#print(len(test_set))

x, y = trasnform_to_dataset(training_set)
clf.fit(x[:8], y[:8])
print('Training Complete')

#>>> Testing
test_sent = [[('I', 'PRP'), ('have', 'VBP'), ('to', 'TO'), ('go', 'VB'), ('to', 'TO'), ('soccer', 'VB'), ('tomorrow', 'NN'), ('at', 'IN'), ('5', 'CD'), ('.', '.')]]
x_t, y_t = trasnform_to_dataset(test_sent)
print('Accuracy: ', clf.score(x_t, y_t))
#test = pos_tag_learn(word_tokenize('I have to go to soccer practice at 2.'))

# [(I, PRP), (have, VB]
