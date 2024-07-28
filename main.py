import requests
import json
import schedule
import time
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

# Define your interests here
interests = { 
    'ai',
    'information technology security',
    'interest rate',
    'house mortgage',
    'rate cuts',
    'inflation',
    'bitcoin'
}

# Replace with your Discord webhook URL
DISCORD_WEBHOOK_URL = ''

# Define the Swedish timezone
SWEDISH_TIMEZONE = pytz.timezone('Europe/Stockholm')

def send_to_discord(message):
    """Send a message to the specified Discord webhook."""
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
    """Fetch news headlines from Yahoo News for a specific interest."""
    url = 'https://news.search.yahoo.com/search?q={}'.format(interest)
    response = requests.get(url)
    headlines = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for news_item in soup.find_all('div', class_='NewsArticle'):
            title = news_item.find('h4').text
            link = news_item.find('a')['href']
            message = f"**Title:** {title}\n**Link:** <{link}>"
            headlines.append(message)
    else:
        print(f"Failed to retrieve news for {interest} with status code {response.status_code}")
    return headlines

def split_message(message, limit=2000):
    """Split message into chunks that fit within the character limit."""
    if len(message) <= limit:
        return [message]
    parts = []
    while len(message) > limit:
        part = message[:limit]
        last_newline = part.rfind("\n")
        if last_newline == -1:
            last_newline = limit
        parts.append(message[:last_newline])
        message = message[last_newline:]
    parts.append(message)
    return parts

def fetch_and_send_news():
    """Fetch headlines for all interests and send them to Discord."""
    all_headlines = []
    for interest in interests:
        headlines = get_yahoo_news_headlines(interest)
        if headlines:
            all_headlines.append(f"\n**News for {interest}:**\n" + "\n".join(headlines))
    
    if all_headlines:
        final_message = "\n".join(all_headlines)
        for message_part in split_message(final_message):
            send_to_discord(message_part)

# Schedule the job to run once a day at 12:00 PM Swedish time
schedule.every().day.at("12:00").do(fetch_and_send_news)

def get_current_time_in_swedish_timezone():
    """Get the current time in the Swedish timezone."""
    return datetime.now(SWEDISH_TIMEZONE).strftime("%H:%M:%S")

if __name__ == '__main__':
    print(f"Starting news bot. Current time in Swedish timezone: {get_current_time_in_swedish_timezone()}")
    # Run the scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)
