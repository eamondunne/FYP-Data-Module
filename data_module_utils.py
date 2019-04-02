import requests
import lxml
from bs4 import BeautifulSoup
from textblob import TextBlob
import re
import json
import time


def get_sentiment(text):
    '''
    Function to classify sentiment of text
    using textblob's sentiment method
    '''
    analysis = TextBlob(clean_text(text))
    return analysis


def get_sentiment_text(score):
    # Process sentiment score to value
    if score > 0:
        return 'positive'
    elif score == 0:
        return 'neutral'
    else:
        return 'negative'


def clean_text(text):
    '''
    Function to clean text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())


def post_result(api, result):
    '''
    Function to post results to the backend API
    '''
    requests.post(api, result)

def remove_list_duplicates(duplicate_list):
  return list(dict.fromkeys(duplicate_list))