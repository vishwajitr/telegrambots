import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
import re
import urllib.parse
import requests
import facebook
from selenium import webdriver

# Telegram Credentials
API_ID = '22544328'
API_HASH = 'c9b5f81a263933e3fecce08cc719fa00'
PHONE_NUMBER = '+919702270708'
CHANNEL_USERNAME = 'amazonindiaassociates'

# Telegram Bot Credentials
BOT_TOKEN = '6831241416:AAEamtwesUyXH5NBAGt3gLzMBsabgahGL9o'
TELEGRAM_CHANNEL = '@dealstodayindia001'

# Bitly Credentials
BITLY_ACCESS_TOKEN = '5ce0605d81302ac039faf49be37ec90c843cd62b'

# Facebook Credentials
FACEBOOK_ACCESS_TOKEN = 'EAADjpjJBmTMBO9gWelXNNqVpZAfJKtWk0X8ZAKVeJWtZAC1ZB6eWdgVHEXaPD8oxChhgyIXTF2BAh4dnBUv0JbM4FeBG4xYbUK5GfcGv0Oy5Qno8v31UEwcJZBAkCrpTs4CixcJglv5NLMGCO3kmKTvTBzZBvv5sxuZBGt4YEysiK6oDka9aFRPdE0xCxR0vn3B2zVrRRrvXtSX64hkH3qCTXPQZAZBAaHeV034YkweYZD'
FACEBOOK_PAGE_ID = '105896528030351'

# Session file path
SESSION_FILE = 'telegram_session'

def get_actual_url_with_selenium(redirect_url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(redirect_url)
        actual_url = driver.current_url
        driver.quit()
        return actual_url
    except Exception as e:
        print(f"Selenium URL Error: {e}")
        return None

def urlprocessing(url):
    params = {'tag':'offerscode08-21', 'affid': 'vishwajit8', 'ref': 'offerscode21'}
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)

def shorten_url(long_url):
    bitly_api_url = 'https://api-ssl.bitly.com/v4/shorten'
    headers = {
        'Authorization': f'Bearer {BITLY_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {'long_url': long_url}
    
    try:
        response = requests.post(bitly_api_url, headers=headers, json=data)
        return response.json()['link'] if response.status_code == 200 else None
    except Exception as e:
        print(f"Bitly URL Shortening Error: {e}")
        return None

def process_links(text):
    url_regex = r'https?://\S+'
    urls = re.findall(url_regex, text)

    for url in urls:
        new_link = get_actual_url_with_selenium(url)
        if new_link:
            new_url = urlprocessing(new_link)
            shortened_url = shorten_url(new_url)
            if shortened_url:
                text = text.replace(url, shortened_url)
    return text

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    return requests.post(url, params=params).json()

def post_to_facebook(message):
    try:
        graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
        graph.put_object(parent_object=FACEBOOK_PAGE_ID, connection_name='feed', message=message)
        print("Message posted to Facebook successfully")
    except Exception as e:
        print(f"Facebook Posting Error: {e}")

async def get_telegram_client():
    # Check if session file exists
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            session_string = f.read().strip()
        return TelegramClient(StringSession(session_string), API_ID, API_HASH)
    
    # If no session, create new client and prompt for login
    client = TelegramClient('new_session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    # Save session string for future use
    session_string = client.session.save()
    with open(SESSION_FILE, 'w') as f:
        f.write(session_string)
    
    return client

async def fetch_and_process_messages():
    try:
        async with await get_telegram_client() as client:
            entity = await client.get_entity(CHANNEL_USERNAME)
            messages = await client.get_messages(entity, limit=1)

            for message in messages:
                if message.text:
                    processed_text = process_links(message.text)
                    send_telegram_message(BOT_TOKEN, TELEGRAM_CHANNEL, processed_text)
                    post_to_facebook(processed_text)
    except Exception as e:
        print(f"Message Fetching Error: {e}")

async def main():
    while True:
        await fetch_and_process_messages()
        await asyncio.sleep(60)  # 1 minutes

if __name__ == '__main__':
    asyncio.run(main())