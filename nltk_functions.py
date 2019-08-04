import nltk
import re

def lexical_diversity(text):
    return len(set(text)) / len(text)

def percentage(token, text):
    return 100 * text.count(token) / len(text)



def mySentTokenize(text):
    nltk_sents = nltk.sent_tokenize(text)

    join_s1_indexes = [];
    for i, s in enumerate(nltk_sents):
        if re.match(r'^\.$', s):
            join_s1_indexes.append(i-1)
        elif re.match(r'^[a-z]', s) and re.match(r'^\.$', nltk_sents[i-1]):
            join_s1_indexes.append(i-1)
    rejoinSents(nltk_sents, join_s1_indexes)

    join_s1_indexes = []
    for i, s in enumerate(nltk_sents):
        if re.search(r'\([^)]+$', s):
            join_s1_indexes.append(i)
        if re.match(r'^[a-z]', s):
            join_s1_indexes.append(i-1)
        if re.search(r'\b[vc]\.$', s):
            join_s1_indexes.append(i)
        if re.match(r'^\[\d{1,2}\]', s) and i != 0:
            join_s1_indexes.append(i-1)
    rejoinSents(nltk_sents, join_s1_indexes)

    final_sents = nltk_sents
    return final_sents

# def mySort(x):
#     return x[1]

def rejoinSents(sents, join_s1_indexes, joiner = " "):
    join_s1_indexes = sorted(set(join_s1_indexes), reverse=True)
    for s1_i in join_s1_indexes:
        s2_i = s1_i + 1
        sents[s1_i] = sents[s1_i] + joiner + sents[s2_i]
        del sents[s2_i]





# class IndexedText(object):
#
#     def __init__(self, stemmer, text):
#         self._text = text
#         self._stemmer = stemmer
#         self._index = nltk.Index((self._stem(word), i)
#                                  for (i, word) in enumerate(text))
#
#     def concordance(self, word, width=40):
#         key = self._stem(word)
#         wc = int(width/4)                # words of context
#         for i in self._index[key]:
#             lcontext = ' '.join(self._text[i-wc:i])
#             rcontext = ' '.join(self._text[i:i+wc])
#             ldisplay = '{:>{width}}'.format(lcontext[-width:], width=width)
#             rdisplay = '{:{width}}'.format(rcontext[:width], width=width)
#             print(ldisplay, rdisplay)
#
#     def _stem(self, word):
#         return self._stemmer.stem(word).lower()
#
#     # Use:
#     # porter = nltk.PorterStemmer()
#     # grail = nltk.corpus.webtext.words('grail.txt')
#     # text = IndexedText(porter, grail)
#     # print(text.concordance('lie'))

# text = 'That U.S.A. poster-print costs $12.40...'
# pattern = r'''(?x)    # set flag to allow verbose regexps
#     ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
#     | \w+(-\w+)*        # words with optional internal hyphens
#     | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
#     | \.\.\.            # ellipsis
#     | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
#     '''
# nltk.regexp_tokenize(text, pattern)
# Note: We can evaluate a tokenizer by comparing the resulting tokens with a wordlist, and reporting any tokens that don't appear in the wordlist, using set(tokens).difference(wordlist). You'll probably want to lowercase all the tokens first.
