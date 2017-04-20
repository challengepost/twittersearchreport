from TwitterSearch import *
import time
import string
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
from os import environ

from flask import request, session, Flask, render_template, Response, redirect, url_for

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import CompileError

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Initialise the Flask app ##
application = Flask(__name__)
application.config['PROPAGATE_EXCEPTIONS'] = True

@application.route('/', defaults={'path': None})
@application.route('/<path:path>')
def main(path=None):
    scope = ['https://spreadsheets.google.com/feeds']

    pk = "-----BEGIN PRIVATE KEY-----{key}-----END PRIVATE KEY-----\n".format(key=environ['PK'])

    key_dict = {
        "type": "service_account",
        "project_id": "devposthackathontweets",
        "private_key_id": "1d02a04353966c7d0f48be5dc6780c20177f96bd",
        "private_key": pk,
        "client_email": "hackathon-manager@devposthackathontweets.iam.gserviceaccount.com",
        "client_id": "105326323772464143676",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/hackathon-manager%40devposthackathontweets.iam.gserviceaccount.com"
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Hackathon Twitter").sheet1

    # Extract and print all of the values
    sheets_data = sheet.get_all_records()

    if path is None:
        return render_template('index.html', payload=sheets_data)
    else:
        c = getClient(path, sheets_data)
        k = getKeywords(path, sheets_data)
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

def getKeywords(path, sheets_data):
    for item in sheets_data:
        print item
        #hackathon = 0
        if item['hackathon_slug'] == path:
            hackathon = item

    kw = hackathon['hackathon_tags'].split(", ")
    return kw

def getClient(path, sheets_data):
    client = None
    for item in sheets_data:
        if item['hackathon_slug'] == path:
            client = item['hackathon_name']
    return client
