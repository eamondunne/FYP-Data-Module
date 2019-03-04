import json
import requests
import re
from textblob import TextBlob
import time


class reddit_comments(object):
    def __init__(self):
        self.URL = 'http://localhost:3000/api/bitcoin_reddit_comments_sentiments'

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
        positive = 0
        neutral = 0
        negative = 0

        # Get Date of Comments
        timestamp = time.strftime(
            '%Y-%m-%d', time.localtime(raw_comments[0]["created_utc"]))

        for i in raw_comments:
            score = self.process_comment(i)
            if(score is 'positive'):
                positive += 1
            if(score is 'neutral'):
                neutral += 1
            if(score is 'negative'):
                negative += 1
        
        result = {
            "date": timestamp,
            "num_positive": positive,
            "num_neutral": neutral,
            "num_negative": negative
        }
        self.post_result(result)

    def process_comment(self, comment):
        """
        Gets comment sentiment, formats and returns result
        """
        sentiment_score = self.get_comment_sentiment(comment['body'])

        # Process sentiment score to value
        if sentiment_score > 0:
            return 'positive'
        elif sentiment_score == 0:
            return 'neutral'
        else:
            return 'negative'

    def post_result(self, result):
        requests.post(self.URL, result)

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


def main():
    r = reddit_comments()
    for i in range(0, 365):
        r.get_comments(1000, i)
        print("Day: " + str(i))


if __name__ == "__main__":
    # calling main function
    main()
