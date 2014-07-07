import random
import hashlib
import calendar
import datetime
from threading import Timer
import os

import praw
from boto.dynamodb2.table import Table


r = praw.Reddit(user_agent='RedditABTest-0.1 by FlightOfStairs')
r.login(os.environ['REDDIT_USERNAME'], os.environ['REDDIT_PASSWORD'])

records = Table('redditabtest')

trigger_rate = 0.01


def allocate(submission, range):
    m = hashlib.sha256()
    m.update(submission.fullname.encode('utf-8'))
    return sum(ord(c) for c in m.digest()) % int(range)


def vote(submission, score):
    if score == 1:
        submission.upvote()
    if score == -1:
        submission.downvote()

    records.put_item(data={
        "id": submission.fullname,
        "timestamp": calendar.timegm(datetime.datetime.utcnow().utctimetuple()),
        "vote": score,
        "submission_timestamp": submission.created_utc
    })
    print "\nRecorded vote " + str(score) + " for " + submission.fullname + " - " + submission.title + " " + submission.short_link

def scheduleVote(submission, score):
    Timer(random.randint(1, 300), lambda: vote(submission, score), ()).start()


for submission in praw.helpers.submission_stream(r, 'all', limit=None):
    if not allocate(submission, 1 / trigger_rate) == 0:
        continue
    else:
        score = allocate(submission, 3) - 1
        scheduleVote(submission, score)
