import nltk as nl
from HTMLParser import HTMLParser

# import httplib2
# import beautifulsoup as bs
stopwords = set()
with open('english_stopwords.txt') as f:
    for line in f:
        stopwords.add(line.strip())

stopwords |= set([",",";",":","?","=","+","."])

def tokenize_title (title):
	tokens = nl.tokenize.word_tokenize(strip_tags(title))
	words = [w for w in tokens if w.lower() not in stopwords]
	return words

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


