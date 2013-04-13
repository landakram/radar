import urllib
from readability.readability import Document
# pip install readability-lxml
from naive_bayes import strip_tags

def get_extract(*args,**kwargs):
	# loads webpage and gets content
	html = urllib.urlopen(kwargs.get('url')).read()
	readable_article = Document(html).summary()
	return strip_tags(readable_article)