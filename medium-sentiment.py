import requests
import lxml
import pprint
from bs4 import BeautifulSoup
import json
from data_module_utils import *
from statistics import mean
import datetime as dt

medium_feed = 'https://medium.com/tag/bitcoin/archive/'
api_url = 'http://localhost:3000/api/bitcoin_medium_sentiments'

num_days = 365

# TODO: put an article limit in...


def main():
    print("Starting:")
    data = []
    total_run_start = time.time()
    for i in range(13, num_days):
        start_time = time.time()
        links = strip_links(medium_feed, i)
        links = remove_list_duplicates(links)
        link_iter = 0
        for link in links:
            print("ARTICLE:", link)
            if link_iter is 20:
                break
            single_link_start = time.time()
            processed = process_link(link)
            if processed is not -1:
                data.append(processed)
                link_iter += 1
            single_link_end = time.time()
            print("Single Link Process Time: ", str(
                single_link_end - single_link_start))

        analysis_time = time.time()
        result = average_sentiment(data, i)
        post_result(api_url, result)
        end_time = time.time()
        print("----------")
        print("Day Run Time: " + str(end_time - start_time))
        print("Analysis Time: " + str(end_time - analysis_time))
        print("Link Process Time: " + str(analysis_time - start_time))
    total_run_end = time.time()
    print("Total Runtime: ", str(total_run_end - total_run_start))


def strip_links(link, day):
    date = (dt.datetime.today() - dt.timedelta(days=day)
            ).date().strftime('%Y/%m/%d')

    feed = requests.get(medium_feed + date, verify=False).text
    feed_soup = BeautifulSoup(feed, 'lxml')
    links = []
    links = [a.get('href') for a in feed_soup.find_all(
        'a', {"data-action": 'open-post'}, href=True)]
    return links


def process_link(link):
    content = requests.get(link, verify=False).text
    soup = BeautifulSoup(content, 'html5lib')
    text_list = soup.find_all('p')
    if not text_list:
        return -1
    text_block = ''
    for text in text_list:
        text_block += text.getText()
    data = {
        'text': text_block,
    }
    return data


def average_sentiment(data, day):
    '''
    Calculates the average sentiment of a given batch of comments
    '''
    polarity_list = []
    subjectivity_list = []
    # Calculates the Polarity & Subjectivity of each comment then calculates the average
    for t in data:
        text = t['text']
        comment_polarity = get_sentiment(text).sentiment.polarity
        comment_subjectivity = get_sentiment(text).sentiment.subjectivity
        polarity_list.append(comment_polarity)
        subjectivity_list.append(comment_subjectivity)
    mean_polarity = mean(polarity_list)
    mean_subjectivity = mean(subjectivity_list)
    sentiment_text = get_sentiment_text(mean_polarity)
    date = (dt.datetime.today() - dt.timedelta(days=day)
            ).date().strftime('%Y/%m/%d')
    processed_comment = {
        "date": date,
        "polarity": mean_polarity,
        "subjectivity": mean_subjectivity,
        "sentiment": sentiment_text,
        "num_articles": len(data)
    }
    return processed_comment


if __name__ == "__main__":
    main()
