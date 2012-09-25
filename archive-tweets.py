#!/usr/bin/python

import tweepy
import pytz
import os

# Parameters.
me = 'username'
urlprefix = 'http://twitter.com/%s/status/' % me
tweetdir = os.environ['HOME'] + '/Dropbox/twitter/'
tweetfile = tweetdir + 'twitter.txt'
idfile = tweetdir + 'lastID.txt'
datefmt = '%B %-d, %Y at %-I:%M %p'
homeTZ = pytz.timezone('US/Central')
utc = pytz.utc

def setup_api():
  """Authorize the use of the Twitter API."""
  a = {}
  with open(os.environ['HOME'] + '/.twitter-credentials') as credentials:
    for line in credentials:
      k, v = line.split(': ')
      a[k] = v.strip()
  auth = tweepy.OAuthHandler(a['consumerKey'], a['consumerSecret'])
  auth.set_access_token(a['token'], a['tokenSecret'])
  return tweepy.API(auth)

# Authorize.
api = setup_api()

# Get the ID of the last downloaded tweet.
with open(idfile, 'r') as f:
  lastID = f.read().rstrip()

# Collect all the tweets since the last one, up to 200.
tweets = api.user_timeline(me, since_id=lastID, count=200, include_rts=True)

# If necessary, collect any tweets in excess of those 200.
while len(tweets) >= 1:
    maxID = tweets[-1].id_str
    chunk = api.user_timeline(me, since_id=lastID, max_id=maxID,
                              count=200, include_rts=True)
    if len(chunk) == 1:
        break
    else:
        tweets.extend(chunk[1:]) # max_id is inclusive

# Write them out to the twitter.txt file.
with open(tweetfile, 'a') as f:
    for t in reversed(tweets):
      ts = utc.localize(t.created_at).astimezone(homeTZ)
      lines = ['',
               t.text,
               ts.strftime(datefmt).decode('utf8'),
               urlprefix + t.id_str,
               '- - - - -',
               '']
      f.write('\n'.join(lines).encode('utf8'))
      lastID = t.id_str

# Update the ID of the last downloaded tweet.
with open(idfile, 'w') as f:
  lastID = f.write(lastID)
