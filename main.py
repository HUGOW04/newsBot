from bs4 import BeautifulSoup
import requests
import json
import schedule
import time
from datetime import datetime
import pytz

interests = {'bitcoin'}

DISCORD_WEBHOOK_URL = 'YOUR_DISCORD_WEBHOOK_URL'  # Replace with your Discord webhook URL
SWEDISH_TIMEZONE = pytz.timezone('Europe/Stockholm')

def send_to_discord(message):
    data = {
        "content": message,
        "username": "NewsBot"
    }
    result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Failed to send message to Discord: {err}")
    else:
        print(f"Message delivered to Discord, code {result.status_code}.")

def get_yahoo_news_headlines(interest):
    url = 'https://news.search.yahoo.com/search?q={}'.format(interest)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for news_item in soup.find_all('div', class_='NewsArticle'):
            title = news_item.find('h4').text
            time = news_item.find('span', class_='fc-2nd').text
            # Clean time text
            time = time.replace('·', '').strip()
            link = news_item.find('a')['href']  # Get the link to the news article
            message = f"**Title:** {title}\n**Time:** {time}\n**Link:** {link}\n"
            send_to_discord(message)
    else:
        print(f"Failed to retrieve news for {interest} with status code {response.status_code}")

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
    print(f"Starting news bot. Current time in Swedish timezone: {get_current_time_in_swedish_timezone()}")
    while True:
        schedule.run_pending()
        time.sleep(1)
