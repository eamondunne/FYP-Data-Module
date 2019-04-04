import twint
import data_module_utils
import datetime as dt
from data_module_utils import *
from statistics import mean
import json

api_url = 'http://localhost:3000/api/bitcoin_twitter_sentiments'

num_days = 2
limit = 100

def main():
  print("Starting:")
  total_start = time.time()
  for i in range(0, num_days):
    startTime = time.time()
    tweets = get_tweets_daily("#bitcoin", i, limit)
    api_call_time = time.time()
    processed = process_tweets(tweets)
    process_time = time.time()
    post_result(api_url, processed)
    end_time = time.time()
    print(processed)
    print("---------")
    print("API Call Time: " + str(api_call_time - startTime))
    print("Process Time: " + str(process_time - api_call_time))
    print("Total Time: " + str(end_time - startTime))
    print("---------")


def get_tweets_daily(searchTerm, day, limit):
  # Calculate and Format Date frame
  since = (dt.datetime.today() - dt.timedelta(days=day + 1)).date().strftime('%Y-%m-%d')
  until = (dt.datetime.today() - dt.timedelta(days=day)).date().strftime('%Y-%m-%d')
  c = twint.Config()
  c.Search = searchTerm
  c.Verified = True
  c.Limit = limit
  c.Format = "{tweet}"
  c.Since = since
  c.Until = until
  c.Store_object = True
  c.Hide_output = True
  twint.run.Search(c)
  return twint.output.tweets_object

def process_tweets(tweets):
    '''
    Calculates the average sentiment of a given batch of tweets
    '''
    polarity_list = []
    subjectivity_list = []
    for tweet in tweets:
        text = tweet.tweet
        comment_polarity = get_sentiment(text).sentiment.polarity
        comment_subjectivity = get_sentiment(text).sentiment.subjectivity
        polarity_list.append(comment_polarity)
        subjectivity_list.append(comment_subjectivity)
    mean_polarity = mean(polarity_list)
    mean_subjectivity = mean(subjectivity_list)
    sentiment_text = get_sentiment_text(mean_polarity)
    processed_block = {
        "date": tweet.datestamp,
        "polarity": mean_polarity,
        "subjectivity": mean_subjectivity,
        "sentiment": sentiment_text,
        "num_tweets": len(tweets)
    }
    return processed_block


if __name__ == "__main__":
    # calling main function
    main()
