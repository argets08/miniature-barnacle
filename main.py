import array
import json
import logging
from datetime import datetime, timedelta
from termcolor import colored, cprint

import requests
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
API_KEY = ""
API_SECRET = ""
ALPACA_BASE_URL = 'https://data.alpaca.markets'
logging.getLogger("transformers").setLevel(logging.ERROR)

@app.get("/")
async def root():
    return {"message": "Hello World"}

def extract_alpaca_news(apiKey, apiSecret, symbols, startDate, endDate):
    url = f'{ALPACA_BASE_URL}/v1beta1/news?start={startDate}&end={endDate}&symbols={symbols}&limit=50'
    headers = {'content-type': 'application/json', 'Apca-Api-Key-Id': apiKey, 'Apca-Api-Secret-Key': apiSecret}
    response = requests.get(url, headers=headers)
    # print(json.loads(response.text))
    return json.loads(response.text)

def get_article_titles(news):
    article_titles = [article['headline'] for article in news['news']]
    # print(article_titles)
    return article_titles

def get_sentiment_list(article_titles):
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    revision = "af0f99b"
    classifier = pipeline('sentiment-analysis', model=model_name, revision=revision)
    sentiment_list = []
    for title in article_titles:
        sentiment = classifier(title)
        # print(sentiment)
        if (sentiment[0]['score'] >= 0.9):
            sentiment_list.append(sentiment[0])
    return sentiment_list

def print_stock_sentiment(stock, average_score, overall_sentiment, color):
     # Print the results
    print(colored(f"Stock: {stock}",'blue'))
    print(f"Average Sentiment Score: {average_score:.4f}")
    print(colored(f"Overall Sentiment: {overall_sentiment}", color))

@app.post("/stock_list/")
async def stock_list(list_stock: str):
    today = datetime.today().weekday()
    if today == 0:
        hours = 8
    else:
        hours = 12
    print(f"Hours: {hours}")
    start_date = (datetime.today() - timedelta(hours)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')
    list_of_stocks = list_stock.split(",")
    for stock in list_of_stocks:
        stock = stock.strip()
        article_titles = []
        neg_sentiment_score = 0
        pos_sentiment_score = 0
        neg_score_count = 0
        pos_score_count = 0
        news = extract_alpaca_news(API_KEY, API_SECRET, stock, start_date, end_date)
        article_titles = get_article_titles(news)
        sentiment_list_for_stock = get_sentiment_list(article_titles)

        for sentiment in sentiment_list_for_stock:
            if sentiment['label'] == 'NEGATIVE':
                neg_sentiment_score += sentiment['score']
                neg_score_count += 1
            else:
                pos_sentiment_score += sentiment['score']
                pos_score_count += 1
        if neg_score_count > pos_score_count and neg_score_count != 0:
            average_score = neg_sentiment_score / neg_score_count
            # overall_sentiment = 'NEGATIVE'
            color = 'red'
            # print_stock_sentiment(stock, average_score, overall_sentiment, color)
        elif pos_score_count > neg_score_count and pos_score_count != 0:
            average_score = pos_sentiment_score / pos_score_count
            overall_sentiment = 'POSITIVE'
            color = 'green'
            if (average_score > 0.9950):
                print_stock_sentiment(stock, average_score, overall_sentiment, color)

@app.post("/sentiment_graph/")
async def sentiment_graph(symbol: str):
    # TODO document why this method is empty
    # create a graph of the sentiment over time and trend iteratively. Use a local small db? or just a csv file?
    pass