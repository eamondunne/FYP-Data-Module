import json
import requests
import re
from textblob import TextBlob
import time

class reddit_comments(object):
    def __init__(self):
        self.URL = 'http://localhost:3000/api/bitcoin_reddit_comments'

    def clean_comment(self, comment):
        '''
        Utility function to clean text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", comment).split())

    def get_comment_sentiment(self, comment):
        '''
        Utility function to classify sentiment of comment
        using textblob's sentiment method
        '''
        analysis = TextBlob(self.clean_comment(comment))
        return analysis.sentiment.polarity

    def process_comment(self, comment):
        """
        Gets comment sentiment, formats and posts to API
        """
        sentiment_score = self.get_comment_sentiment(comment['body'])

        # Process sentiment score to value
        if sentiment_score > 0:
            sentiment_val = 'positive'
        elif sentiment_score == 0:
            sentiment_val = 'neutral'
        else:
            sentiment_val = 'negative'

        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(comment['created_utc']))

        # Create formatted dictionary of comment
        cleaned_comment = {
          "body": str(comment['body']),
          "timestamp": str(timestamp),
          "sentiment_score": sentiment_score,
          "sentiment_value": str(sentiment_val)
        }
        # Post comment to REST API
        self.post_comment(cleaned_comment)

    def post_comment(self, comment):
        request = requests.post(self.URL, comment)

    def get_comments(self, size, dayframe):
        """
        Retrieves comments from the pushshift API
        """
        before_time = '&before=' + str(dayframe) + 'd'
        after_time = '&after=' + str(dayframe + 1) + 'd'
        timeframe = before_time + after_time
        url = 'https://api.pushshift.io/reddit/comment/search/?subreddit=bitcoin&size=' + \
            str(size)
        url = url + timeframe
        request = requests.get(url)
        json = request.json()
        raw_comments = json['data']
        for i in raw_comments:
            self.process_comment(i)


def main():
    r = reddit_comments()
    for i in range(0,365):
        r.get_comments(200, i)
        print("Day: " + str(i))


if __name__ == "__main__":
    # calling main function
    main()
