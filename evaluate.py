import praw
import calendar
import datetime
from boto.dynamodb2.table import Table

table = Table('redditabtest')

r = praw.Reddit(user_agent='RedditABTest-0.1 by FlightOfStairs')

def upsAndDowns(score, ratio):
    ratio -= 0.000001 # avoids div by zero, result is rounded anyway
    return round((ratio * score) / (2 * ratio - 1)), \
           round((score - ratio * score)/(2 * ratio - 1))

vote_name = {-1: "DOWN", 0: "NONE", 1: "UP"}

file = open('scores.csv', 'w')

file.write("id,vote,vote_latency,age,score,ratio,ups,downs\n")

for record in table.scan():
    id = record['id']
    vote = record['vote']
    age = calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - record['submission_timestamp']
    vote_latency = record['timestamp'] - record['submission_timestamp']

    submission = r.get_submission(submission_id=id[3:])

    score = submission.score
    ratio = submission.upvote_ratio

    ups, downs = upsAndDowns(score, ratio)

    line = id + "," + vote_name[vote] + "," + str(vote_latency) + "," + str(age) + "," + str(score) + "," + str(ratio) + "," + str(ups) + "," + str(downs)

    file.write(line + "\n")
    file.flush()
    print line

file.close()
