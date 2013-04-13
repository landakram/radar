import feedparser
import datetime
from db import db
from time import mktime

def update_feed(feed):
    recent_entry = feed['entries'][0]
    print (datetime.datetime.now() - recent_entry['date_added']).seconds
    if (datetime.datetime.now() - recent_entry['date_added']).seconds < 60*5:
        return

    print "Updating feeds..."
    recent_entry_url = recent_entry['url']

    d = feedparser.parse(feed['url'])
    entries = d.entries
    filtered_entries = entries

    for i, entry in enumerate(entries):
        if entry['link'] == recent_entry_url:
            filtered_entries = filtered_entries[:i]
            break

    filtered = [create_entry(parser=e) for e in filtered_entries]
    # Cut off at 100 entries
    feed['entries'] = (filtered + feed['entries'])[:100]

def create_feed(*args, **kwargs):
    # parse the url from the arguments
    url              = kwargs.get('url')
    found_feed       = feedparser.parse(url)
    feed = db.Feed.find_one({'url' : found_feed.url})
    if feed:
        return feed
    else:
        # parsed feed creates new feed object if feed does
        # not exist yet.
        feed             = db.Feed()
        feed.title       = found_feed.feed.title
        feed.url         = found_feed.url
        feed.description = found_feed.feed.description
        feed.published   = datetime.datetime.fromtimestamp(mktime(found_feed.feed.updated_parsed))
        feed.date_added  = datetime.datetime.now()
        feed.entries     = []
        # iterate through entries (this method should)
        # be isolated to allow updating of feeds later on
        for found_entry in found_feed.entries:
            entry = create_entry(parser=found_entry)
            feed.entries.append(entry)

        feed.save()
        return feed

def create_entry(*args, **kwargs):
    # creates a new entry either from parse data,
    # or by inputing title, desc, url...
    parsed_entry = kwargs.get('parser')
    if parsed_entry:
        entry = db.Entry.find_one({'url': parsed_entry.link})
        if entry:
            return entry
        else:
            entry             = db.Entry()
            entry.date_added  = datetime.datetime.now()
            entry.title       = parsed_entry.title
            entry.description = parsed_entry.description
            entry.url         = parsed_entry.link
            entry.published   = datetime.datetime.fromtimestamp(mktime(parsed_entry.published_parsed))
            entry.save()
            return entry
    else:
        entry = db.Entry.find_one({'url':kwargs.get('url')})
        if entry:
            return entry
        else:
            entry             = db.Entry()
            entry.date_added  = datetime.datetime.now()
            entry.title       = kwargs.get('title')
            entry.url         = kwargs.get('url')
            entry.description = kwargs.get('description')
            entry.published   = kwargs.get('published')
            entry.save()
            return entry
            # can get pubdate through parsing... next time perhaps
