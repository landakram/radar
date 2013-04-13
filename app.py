import functools

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from mongokit import ObjectId
import requests
import operator as op
import json
from feeds import update_feed, create_feed
import naive_bayes as nb
from db import db
import web_parsing as webp
import datetime
from naive_bayes import stopwords

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

def login_required(view):
    @functools.wraps(view)
    def decorated_view(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('index'))
        user = db.User.get_from_id(user_id)
        return view(user=user, *args, **kwargs)
    return decorated_view

@app.route('/keyword', methods=['POST'])
@login_required
def add_good_keyword(user=None):
    token = unicode(request.form['keyword'])

    if token in stopwords:
        return jsonify(success=True)

    is_bad = int(request.form['bad']) == 1
    if is_bad:
        cls = db.BadToken
    else:
        cls = db.GoodToken
    g_token = cls.find_one({"user_id": user._id, "value": token})
    if not g_token:
        g_token = cls()
        g_token['value'] = token
        g_token['count'] = 0
        g_token['user_id'] = user._id

    g_token['count'] += 3
    g_token.save()
    return jsonify(success=True)

@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        user = None
        return render_template('index.html')
    else:
        user = db.User.get_from_id(user_id)
        entries = []
        if user:
            for feed in user.feeds:
                update_feed(feed)
                user.save()

                for entry in feed['entries']:
                    entry['feed_title'] = feed['title']
                    hidden_entries = user.hidden_entries
                    if entry['_id'] not in hidden_entries:
                        entries.append(entry)
            entries.sort(key=lambda e: compute_score(user=user, entry=e), reverse=True)

        # strftime('%A, %B %d, %I:%M%p')
        return render_template('show_entries.html', user=user, entries=entries)


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    code = request.args.get('code')
    data = {
        'app_id': app.config['CLEF_APP_ID'],
        'app_secret': app.config['CLEF_APP_SECRET'],
        'code': code
    }
    response = requests.post('https://clef.io/api/v1/authorize', data=data)
    json_response = json.loads(response.text)

    if json_response.get('error'):
        return json_response['error']

    token = json_response['access_token']
    response = requests.get('https://clef.io/api/v1/info?access_token=%s' % token)
    json_response = json.loads(response.text)

    if json_response.get('error'):
        return json_response['error']

    user_info = json_response['info']

    # Look up the user
    user = db.User.find_one({'clef_id': long(user_info['id'])})
    if not user:
        user = db.User()
        user.email = user_info['email']
        user.first_name = user_info['first_name']
        user.clef_id = long(user_info['id'])
        user.feeds = []

        user.save()

    session['user_id'] = user._id
    return redirect(url_for('index'))


@app.route('/test')
def test(user=None):
    entries = db.Entry.find()
    return repr([entry for entry in entries])

@app.route('/feed', methods=['POST'])
@login_required
def add_feed(user=None):
    feed_url = request.form['url']
    feed = create_feed(url=feed_url)
    user.feeds.append(feed)
    user.save()
    return redirect(url_for('index'))


@app.route('/log_click', methods=['GET'])
@login_required
def log_click(user=None):
    entry = db.Entry.get_from_id(ObjectId(request.args['entry_id']))
    is_bad = int(request.args['bad']) == 1
    if is_bad:
        create_tokens(entry=entry, user=user, good=False)

        user.hidden_entries.append(entry['_id'])
        user.save()

        return redirect(url_for('index'))
    else:
        create_tokens(entry=entry, user=user, good=True)
        return redirect(entry.url)


def compute_score(*args,**kwargs):
    time_norm = 1-float((kwargs.get('entry')["published"]-(datetime.datetime.now()-datetime.timedelta(days=1))).seconds)/86400.0
    naive_bayes_result = naive_bayes(user=kwargs.get('user'),entry=kwargs.get('entry'))
    bayes_norm = (naive_bayes_result["good"]-naive_bayes_result["bad"]) if naive_bayes_result["bad"]<0.5 else 0
    sorted_important_words = sorted(naive_bayes_result["important_words"], key=lambda e: e["frequency"], reverse=True)
    kwargs.get('entry')["keywords"] = ([w["value"] for w in sorted_important_words][:5]) if (sorted_important_words) else []
    # kwargs.get('entry').save()
    kwargs.get('user').save()
    return (time_norm**2+bayes_norm**2)**0.5


def entry_unique_tokens(entry):
    tokens = nb.tokenize_title(entry['title']) + nb.tokenize_title(entry['description'])
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
        if kwargs.get('good') == True:
            # good token
            g_token = db.GoodToken.find_one({"user_id": user._id, "value": utoken})
            if g_token:
                g_token.count += count
            else:
                g_token = db.GoodToken()
                g_token.value = utoken
                g_token.count = count
                g_token.user_id  = user._id

            g_token.save()
        else:
            # bad token
            b_token = db.BadToken.find_one({"user_id": user._id, "value": utoken})
            if b_token:
                b_token.count += count
            else:
                b_token = db.BadToken()
                b_token.value = utoken
                b_token.count = count
                b_token.user_id  = user._id

            b_token.save()
    return unique_tokens

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


if __name__ == '__main__':
    app.run(debug=True)
