# NewsBot

NewsBot is a simple Python script that fetches daily news headlines based on your interests and sends them to a Discord channel via a webhook. The bot runs automatically every day at 12:00 PM Swedish time.

## Features
- Fetches news headlines from Yahoo News.
- Filters news based on user-defined interests.
- Sends alerts via a Discord webhook.
- Runs automatically every day at 12:00 PM.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/newsbot.git
   cd newsbot
   ```

2. **Edit the script:**
   Open the Python script and modify the following variables:
   
   - Set `DISCORD_WEBHOOK_URL` to your actual Discord webhook URL.
   - Modify `interests` to include the news topics you want to track:
     ```python
     interests = { 
         'your topic here',
         'another topic',
         'more topics'
     }
     ```

3. **Run the bot:**
   ```bash
   python newsbot.py
   ```

## How It Works
- The bot scrapes Yahoo News for headlines matching your interests.
- It formats the headlines and sends them to a Discord webhook.
- Runs every day at 12:00 PM Swedish time.

## Example Discord Output
```
**News for Bitcoin:**
Title: Bitcoin hits new highs
Link: <https://example.com>

**News for Inflation:**
Title: Inflation rates continue to rise
Link: <https://example.com>
```

## Notes
- Ensure you have a working internet connection.
- The bot runs in an infinite loop and checks for news at the scheduled time.

## License
This project is open-source and available under the MIT License.

