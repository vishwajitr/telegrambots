from telethon.sync import TelegramClient
import re
from selenium import webdriver
import urllib.parse
import requests
from telegram import Bot

from datetime import datetime, timedelta
import schedule
import time



# Replace 'YOUR_API_ID', 'YOUR_API_HASH', and 'YOUR_PHONE_NUMBER' with your Telegram API credentials
api_id = '22544328'
api_hash = 'c9b5f81a263933e3fecce08cc719fa00'
phone_number = '9702270708'

# Define the channel username (without '@')
channel_username = 'amazonindiaassociates'


def get_actual_url_with_selenium(redirect_url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
        driver = webdriver.Chrome(options=options)

        driver.get(redirect_url)
        actual_url = driver.current_url

        return actual_url

    except Exception as e:
        print(f"Error: {e}")
        return None


def urlprocessing(url):
    # print(get_actual_url_with_selenium('https://blinks.to/nBeTIPf'))
    link = url
    # link = 'https://www.amazon.in/s?k=diaper+pants&i=baby&rh=p_n_deal_type%3A26921224031&pf_rd_i=1571274031&pf_rd_m=A1VBAL9TL5WCBF&pf_rd_p=2b3a79ac-b26e-4389-b26e-b068eb7c64d8&pf_rd_r=TABGTK6TPP5C0N630HMX&pf_rd_s=merchandised-search-2&ref=DiaperfestbbytilesmainApril_1';
    params = {'tag':'offerscode08-21', 'affid': 'vishwajit8', 'ref': 'offerscode21'}

    url_parts = list(urllib.parse.urlparse(link))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urllib.parse.urlencode(query)

    
    link = urllib.parse.urlunparse(url_parts)
    return link


# Replace 'YOUR_BITLY_ACCESS_TOKEN' with your actual Bitly access token
BITLY_ACCESS_TOKEN = '5ce0605d81302ac039faf49be37ec90c843cd62b'

def shorten_url(long_url):
    # Bitly API endpoint for shortening URLs
    bitly_api_url = 'https://api-ssl.bitly.com/v4/shorten'

    # Headers for the request
    headers = {
        'Authorization': f'Bearer {BITLY_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    # Data for the request
    data = {
        'long_url': long_url,
    }

    # Send POST request to Bitly API to shorten the URL
    response = requests.post(bitly_api_url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the shortened URL from the response
        short_url = response.json()['link']
        return short_url
    

# # Example usage
# short_url = shorten_url(link)
# if short_url:
#     print(f"Shortened URL: {short_url}")
    
    

# Function to replace links in text
def get_links(text):
    # Regular expression to find URLs in text
    url_regex = r'https?://\S+'
    urls = re.findall(url_regex, text)


    # Find all URLs in the text
    for url in urls:
        print(url)
        new_link = get_actual_url_with_selenium(url);
        # print(new_link)
        new_url = urlprocessing(new_link);
        # print(new_url)
        new_url2 = shorten_url(new_url);            
        # print(new_url2)
        if new_url2 is not None:
            text = text.replace(url, new_link)    
        else:
            text = url
    return text





def send_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, params=params)
    return response.json()


def post_message(message):
    bot_token = '6831241416:AAEamtwesUyXH5NBAGt3gLzMBsabgahGL9o'
    chat_id = '@dealstodayindia001'
    send_message(bot_token, chat_id, message)
    

def fetch_messages():
    with TelegramClient('session_name', api_id, api_hash) as client:
        client.start()
        entity = client.get_entity(channel_username)

        # Fetch messages from the channel
        # messages = client.get_messages(entity, limit=10, include_media=True)

        messages = client.get_messages(channel_username, limit=1)

        # Process fetched messages
        for message in messages:
            # Check if the message has text
            if message.text:
                
                
                formatted_text = get_links(message.text)
                print("Text:", formatted_text)
                post_message(formatted_text)
                # # Check if the message has media
                # if message.media:
                #     if message.photo:  # Check if the media is a photo
                #         # print("Photo:", message.photo)
                        # post_message(formatted_text)
            


# Schedule the fetch_messages function to run every 2 hours
# schedule.every(2).hours.do(fetch_messages)
schedule.every(15).minutes.do(fetch_messages)


# Run the scheduler indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)