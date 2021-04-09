from nltk import word_tokenize, pos_tag

def buildTaggedCorpus(raw_data):
    builtData = []
    raw_data = raw_data.split("\n")
    for sentance in raw_data:
        builtSentance = []
        dataTokens = word_tokenize(sentance)
        builtData.append(pos_tag(dataTokens))

    plainTextCorpus = []
    for sentance in builtData:
        _sent = []
        for token in sentance:
            _sent.append(token[0] + '/' + token[1].lower())
        plainTextCorpus.append(' '.join(_sent))

    return plainTextCorpus


def buildTrainingSet(sent_list):
    """sentances: [s1, s2...]"""

    for i, sentance in enumerate(sent_list):
        tokens = word_tokenize(sentance)
        sent_list[i] = tokens
    return sent_list


#.........................
with open('Data/punktTraining.txt', 'r') as f:
    raw = f.read()
    f.close()
newcorpus = buildTaggedCorpus(raw)

with open('Data/ca0.txt', 'w') as f:
    for line in newcorpus:
        f.write(line)
        f.write('\n')
    f.close()
