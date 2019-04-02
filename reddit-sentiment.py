import requests
import lxml
from bs4 import BeautifulSoup
from textblob import TextBlob
import re
import json
import time
from data_module_utils import *
from statistics import mean
import datetime as dt
from calendar import timegm

data_url = 'https://api.pushshift.io/reddit/comment/search/'
api_url = 'http://localhost:3000/api/bitcoin_reddit_comment_sentiments'

def main():
  num_comments = 1000
  num_days = 365
  total_start = time.time()
  print("RUNNING:")
  for i in range(0, num_days):
      startTime = time.time()
      comments = get_hourly_comments("bitcoin", num_comments, i)
      api_call_time = time.time()
      processed_comment = average_comment_sentiment(comments)
      process_time = time.time()
      post_result(api_url, processed_comment)
      end_time = time.time()
      print("---------")
      print("Iteration: " + str(i))
      print("API Call Time: " + str(api_call_time - startTime))
      print("Process Time: " + str(process_time - api_call_time))
      print("Total Time: " + str(end_time - startTime))
  total_end = time.time()
  print("Total Run (seconds): " + str(total_end - total_start))
  print("Total Run (minutes): " + str((total_end - total_start)/60))

def get_hourly_comments(subreddit, size, day):
    '''
      returns comments from a given subreddit, cycling through hours to gather
      more comments since the API restricts to 1000 results
      :param subreddit: Subreddit to retrieve comments from.
      :param size: number of comments to return.
      :param day: Time (in days) from current day. E.G. 100 would be 100 days ago.
    '''
    comments = []
    # Set Subreddit and query size
    subreddit = "?subreddit=" + str(subreddit)
    size = "&size=" + str(size)

    date = dt.datetime.today() - dt.timedelta(days=day)
    date = date.date().strftime('%Y-%m-%d')

    # Cycle through hours in a day to collect more data
    for i in range(0, 24):
      before_queryTime = date + "T{:02}".format(i) + ":59:59"
      before_epoche = timegm(time.strptime(before_queryTime, "%Y-%m-%dT%H:%M:%S"))
      after_queryTime = date + "T{:02}".format(i) + ":00:00"
      after_epoche = timegm(time.strptime(
      after_queryTime, "%Y-%m-%dT%H:%M:%S"))
      before_time = '&before=' + str(before_epoche)
      after_time = '&after=' + str(after_epoche)
      timeframe = before_time + after_time

      # Append arguments to API URL
      url = data_url + subreddit + size + timeframe
      comments += requests.get(url).json()['data']

    return comments
    # Retrieve comments from url & return

def get_daily_comments(subreddit, size, date):
    '''
    returns comments from a given subreddit.
    :param subreddit: Subreddit to retrieve comments from.
    :param size: number of comments to return.
    :param day: Time (in days) from current day. E.G. 100 would be 100 days ago.
    '''
    subreddit = "?subreddit=" + str(subreddit)
    size = "&size=" + str(size)

    before_time = '&before=' + str(date) + 'd'
    after_time = '&after=' + str(date + 1) + 'd'
    timeframe = before_time + after_time

    # Append arguments to API URL
    url = data_url + subreddit + size + timeframe
  
    # Retrieve comments from url & return
    comments = requests.get(url).json()['data']
    return comments

def average_comment_sentiment(comments):
    '''
    Calculates the average sentiment of a given batch of comments
    '''
    polarity_list = []
    subjectivity_list = []
    # Calculates the Polarity & Subjectivity of each comment then calculates the average
    for comment in comments:
        text = comment['body']
        comment_polarity = get_sentiment(text).sentiment.polarity
        comment_subjectivity = get_sentiment(text).sentiment.subjectivity
        polarity_list.append(comment_polarity)
        subjectivity_list.append(comment_subjectivity)
    mean_polarity = mean(polarity_list)
    mean_subjectivity = mean(subjectivity_list)
    sentiment_text = get_sentiment_text(mean_polarity)

    timestamp = time.strftime(
        '%Y-%m-%dT%H:%M:%S', time.localtime(comments[0]['created_utc']))
    processed_comment = {
        "date": str(timestamp),
        "polarity": mean_polarity,
        "subjectivity": mean_subjectivity,
        "sentiment": sentiment_text,
        "num_comments": len(comments)
    }
    return processed_comment

if __name__ == "__main__":
    # calling main function
    main()
