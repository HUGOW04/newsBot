from bs4 import BeautifulSoup
import requests
import json
import schedule
import time
from datetime import datetime
import pytz
from transformers import pipeline
from newspaper import Article
import logging

# Initialize the transformer model for text summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

interests = { 
    'ai',
    'information technology security',
    'interest rate',
    'house mortgage',
    'rate cuts',
    'inflation',
    'bitcoin'
}

DISCORD_WEBHOOK_URL = ''  # Replace with your Discord webhook URL
SWEDISH_TIMEZONE = pytz.timezone('Europe/Stockholm')

# Configure logging
logging.basicConfig(level=logging.INFO)

def send_to_discord(message):
    data = {
        "content": message,
        "username": "NewsBot"
    }
    result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"Failed to send message to Discord: {err}")
    else:
        logging.info(f"Message delivered to Discord, code {result.status_code}.")

def fetch_full_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch article from {url}: {e}")
        return ""
    except Exception as e:
        logging.error(f"Failed to fetch article from {url}: {e}")
        return ""

def get_yahoo_news_headlines(interest):
    url = 'https://news.search.yahoo.com/search?q={}'.format(interest)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='NewsArticle')
        
        # Create a list to hold the articles with their titles and links
        articles = []

        for news_item in news_items:
            title = news_item.find('h4').text
            link = news_item.find('a')['href']  # Get the link to the news article
            articles.append((title, link))

        # Fetch and summarize the full content of the articles
        summarized_articles = []

        for title, link in articles:
            full_text = fetch_full_article(link)
            if full_text:
                try:
                    logging.info(f"Summarizing article: {link} with text length: {len(full_text)}")
                    summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)
                    if summary and isinstance(summary, list) and len(summary) > 0:
                        summarized_text = summary[0]['summary_text']
                        summarized_articles.append((summarized_text, title, link))
                    else:
                        logging.error(f"Summarizer returned an unexpected format for article: {link}")
                except IndexError:
                    logging.error(f"IndexError: Summarizer output is out of range for article: {link}")
                except Exception as e:
                    logging.error(f"Failed to summarize article from {link}: {e}")
        
        # Rank the articles based on the summarized text length
        ranked_articles = sorted(summarized_articles, key=lambda x: len(x[0]), reverse=True)

        # Send the articles
        for summary, title, link in ranked_articles:
            message = f"**Title:** {title}\n**Summary:** {summary}\n**Link:** <{link}>\n"
            send_to_discord(message)
    else:
        logging.error(f"Failed to retrieve news for {interest} with status code {response.status_code}")

def fetch_and_send_news():
    for interest in interests:
        # Send fetching news message to Discord
        send_to_discord(f"\n```Fetching news for {interest}:```\n\n")
        get_yahoo_news_headlines(interest)

# Schedule the job to run once a day at 12:00 PM Swedish time
schedule.every().day.at("12:00").do(fetch_and_send_news)

def get_current_time_in_swedish_timezone():
    return datetime.now(SWEDISH_TIMEZONE).strftime("%H:%M:%S")

if __name__ == '__main__':
    logging.info(f"Starting news bot. Current time in Swedish timezone: {get_current_time_in_swedish_timezone()}")
    while True:
        schedule.run_pending()
        time.sleep(1)
