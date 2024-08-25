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
    try:
        result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=10)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Failed to send message to Discord: {err}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    else:
        print(f"Message delivered to Discord, code {result.status_code}.")

def get_yahoo_news_headlines(interest):
    """Fetch news headlines from Yahoo News for a specific interest."""
    url = 'https://news.search.yahoo.com/search?q={}'.format(interest)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {interest}: {e}")
        return []

    headlines = []
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='NewsArticle')
        if not news_items:
            print(f"No news articles found for {interest}")
        for news_item in news_items:
            title_element = news_item.find('h4')
            link_element = news_item.find('a')
            title = title_element.text if title_element else "No Title"
            link = link_element['href'] if link_element else "#"
            message = f"**Title:** {title}\n**Link:** <{link}>"
            headlines.append(message)
    except Exception as e:
        print(f"Error parsing news articles for {interest}: {e}")
    
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
    try:
        for interest in interests:
            headlines = get_yahoo_news_headlines(interest)
            if headlines:
                all_headlines.append(f"\n**News for {interest}:**\n" + "\n".join(headlines))
        
        if all_headlines:
            final_message = "\n".join(all_headlines)
            for message_part in split_message(final_message):
                send_to_discord(message_part)
    except Exception as e:
        print(f"Error fetching and sending news: {e}")

# Schedule the job to run once a day at 12:00 PM Swedish time
try:
    schedule.every().day.at("12:00").do(fetch_and_send_news)
except schedule.ScheduleError as e:
    print(f"Schedule error: {e}")
except Exception as e:
    print(f"Unexpected error when scheduling the job: {e}")

def get_current_time_in_swedish_timezone():
    """Get the current time in the Swedish timezone."""
    try:
        return datetime.now(SWEDISH_TIMEZONE).strftime("%H:%M:%S")
    except Exception as e:
        print(f"Error getting current time in Swedish timezone: {e}")
        return "Error fetching time"

if __name__ == '__main__':
    try:
        print(f"Starting news bot. Current time in Swedish timezone: {get_current_time_in_swedish_timezone()}")
        # Run the scheduled tasks
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"Error in the scheduling loop: {e}")
    except KeyboardInterrupt:
        print("Program terminated by user.")
    except Exception as e:
        print(f"Unexpected error in the main loop: {e}")
