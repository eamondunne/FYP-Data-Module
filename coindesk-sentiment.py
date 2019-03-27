import requests
import lxml
from bs4 import BeautifulSoup
from textblob import TextBlob
import re
import json
import time
from utils import *
url_link = 'https://www.coindesk.com/wp-json/v1/tag/4742/'
api_link = 'http://localhost:3000/api/bitcoin_coindesk_sentiments'


def process_link(link):
    content = requests.get(link)
    # Catch for non-article links such as youtube
    if "www.coindesk.com" not in content.url:
        print("external url: " + content.url)
        return -1
    content_text = content.text
    content_soup = BeautifulSoup(content_text, 'lxml')
    timestamp = json.loads(content_soup.find(
        'script', type='application/ld+json').text)['datePublished']
    textBlock = content_soup.find_all('p')
    strippedText = ''
    for txt in textBlock:
        if txt.string is not None:
            strippedText += txt.string
    sentiment = get_sentiment(strippedText)
    sentiment_text = get_sentiment_text(sentiment.polarity)
    result = {
        "url": link,
        "date": timestamp,
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "sentiment": sentiment_text
    }
    return result


def strip_links(link):
    feed = requests.get(link).text
    feed_soup = BeautifulSoup(feed, 'lxml')
    links = [a.get('href') for a in feed_soup.find_all('a', href=True)]

    if(len(links) == 0):
        print("Empty Page")
        return -1
    formatted_links = []
    for l in links:
        l = l.replace("\\", "")
        l = l.replace('"', '')
        formatted_links.append(l)
    return formatted_links


print("Running")
'''code to iterate through all pages of API'''
loop = 1
links = 0
while links is not -1:
    startTime = time.time()
    links = strip_links(url_link + str(loop))
    for link in links:
        processed = process_link(link)
        if processed is not -1:
          post_result(api_link, processed)
    endTime = time.time()
    print("---------------")
    print("Iteration: " + str(loop))
    print("Num Posted: " + str(len(links)))
    print("Time Taken:" + str(endTime - startTime))
    print("---------------")
    loop += 1
