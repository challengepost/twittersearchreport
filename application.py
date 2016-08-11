from TwitterSearch import *
import time
import string
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
from os import environ

from flask import request, session, Flask, render_template, Response, redirect, url_for
from flask_cors import CORS, cross_origin

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import CompileError

# Initialise the Flask app ##
application = Flask(__name__)
application.config['PROPAGATE_EXCEPTIONS'] = True


#temp variables

clientlist = [{'slug':'multitouch', 'hackathon':'Lenovo Multi-Touch Multi-Hack'}, {'slug':'fordsmartjourney', 'hackathon':'Ford Smart Journey'}, {'slug':'intelligentworld', 'hackathon':'GE Predix'}, {'slug':'apachespark', 'hackathon':'Apache Spark Makers Build'}, {'slug':'openshift', 'hackathon':'OpenShift Code Healthy'}]

keywords = {'multitouch': ['multitouch.devpost.com', 'j.mp/1QMGD4k', 'Multi-Touch Multi-Hack'], 'fordsmartjourney': ['#FordMxSmartJourney', 'j.mp/1T7uZCi', 'ford smart journey', 'fordsmartjourney.devpost.com'], 'intelligentworld': ['#IntelligentWorld','intelligentworld.devpost.com', 'j.mp/1SiGFrN'], 'apachespark': ['j.mp/22iwfJF', '#SparkBizApps', 'apachespark.devpost.com'], 'openshift': ['j.mp/202KkKz', '#CodeHealthy', 'openshift.devpost.com']}

@application.route('/', defaults={'path': None})
@application.route('/<path:path>')
def main(path=None):
    if path is None:
        return render_template('index.html', clients=clientlist)
    else:
        c = getClient(path)
        k = getKeywords(path)
        d = getTweets(k)
        return render_template('report.html', client=c, data=d)

def getTweets(keywords):
    data=[]
    try:
        ts = TwitterSearch(
              consumer_key = environ['CK'],
              consumer_secret = environ['CS'],
              access_token = environ['AT'],
              access_token_secret = environ['ATS']
           )
        tso = TwitterSearchOrder()
        tso.set_keywords(keywords, or_operator=True)
        for tweet in ts.search_tweets_iterable(tso):

            ts = time.strftime('%m-%d-%y %H:%M', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

            data.append({'date': ts, 'text': tweet['text'], 'avatar': tweet['user']['profile_image_url_https'], 'user': tweet['user']['screen_name'], 'id': tweet['id'], 'rt': tweet['retweet_count']})

        return(data)

    except TwitterSearchException as e:
        print(e)

def getKeywords(path):
    ## this should be a db call (nosql?)
    kw=[]
    for k in keywords[path]:
        #print k
        kw.append(k)
    return kw

def getClient(path):
    client = None
    for c in clientlist:
        if c['slug'] == path:
            client = c['hackathon']
    return client
