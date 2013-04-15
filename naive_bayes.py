import operator as op
import nltk as nl

from HTMLParser import HTMLParser

from db import db

stopwords = set()

with open('english_stopwords.txt') as f:
    for line in f:
        stopwords.add(line.strip())

stopwords |= set([",",";",":","?","=","+","."])

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


def tokenize_title (title):
	tokens = nl.tokenize.word_tokenize(strip_tags(title))
	words = [w for w in tokens if w.lower() not in stopwords]
	return words


def naive_bayes(*args,**kwargs):
    entry            = kwargs.get('entry')
    user             = kwargs.get('user')
    unique_tokens    = entry_unique_tokens(entry)
    all_prob_good    = []
    all_prob_bad     = []
    important_words  = []
    total_bad_count  = float(db.BadToken.find({"user_id": user._id}).count()) or 1.0
    total_good_count = float(db.GoodToken.find({"user_id": user._id}).count()) or 1.0
    for token, count in unique_tokens.iteritems():
        utoken = unicode(token)

        bad_token  = db.BadToken.find_one({"user_id": user._id,  "value": utoken})
        good_token = db.GoodToken.find_one({"user_id": user._id, "value": utoken})

        good_count = float(good_token.count if good_token else 0.0)
        bad_count = float(bad_token.count if bad_token else 0.0)
        good_prob = min(1.0, good_count / total_good_count)
        bad_prob = min(1.0, bad_count / total_bad_count)
        if good_prob == 0 and bad_prob == 0:
            continue

        if good_prob>1.2*bad_prob:
            important_words.append({"value":utoken,"frequency":good_prob})
        prob_token_bad = bad_prob / (good_prob + bad_prob)
        prob_token_good = good_prob / (good_prob + bad_prob)

        all_prob_good.append(prob_token_good)
        all_prob_bad.append(prob_token_bad)
    good_prod = reduce(op.mul, all_prob_good, 1)
    bad_prod = reduce(op.mul, all_prob_bad, 1)
    if good_prod == bad_prod == 0:
        return {"bad":0.5, "good":0.5, "important_words":important_words}
    total_bad = bad_prod / (good_prod + bad_prod)
    total_good = good_prod / (good_prod + bad_prod)
    return {"bad":total_bad, "good":total_good, "important_words":important_words}


def entry_unique_tokens(entry):
    tokens = tokenize_title(entry['title']) + tokenize_title(entry['description'])
#    tokens += nb.tokenize_title(webp.get_extract(url=entry['url']))
    # assigns frequency value to each token:
    unique_tokens = {}
    for w in tokens:
        if w in unique_tokens:
            unique_tokens[w] += 1
        else:
            unique_tokens[w] = 1
    return unique_tokens


def create_tokens(*args,**kwargs):
    # assigns frequency value to each token:
    unique_tokens = entry_unique_tokens(kwargs.get('entry'))
    user = kwargs.get('user')
    for token, count in unique_tokens.iteritems():
        utoken = unicode(token)
        if kwargs.get('good'):
            TokenClass = db.GoodToken
        else:
            TokenClass = db.BadToken

        g_token = TokenClass.find_one({"user_id": user._id, "value": utoken})
        if g_token:
            g_token.count += count
        else:
            g_token = TokenClass()
            g_token.value = utoken
            g_token.count = count
            g_token.user_id  = user._id

        g_token.save()
    return unique_tokens

