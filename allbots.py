import os
import asyncio
import logging
import json
import re
import urllib.parse
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from selenium import webdriver
import facebook
from instagrapi import Client
from datetime import datetime

class MultiChannelTelegramBot:
    def __init__(self, config_path='config.json'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = json.load(file)

        # Telegram Configuration
        self.api_id = self.config['telegram']['api_id']
        self.api_hash = self.config['telegram']['api_hash']
        self.phone_number = self.config['telegram']['phone_number']
        self.channels = self.config['telegram']['channels']
        self.main_group = self.config['telegram']['main_group']

        # Bot Configuration
        self.bot_token = self.config['telegram_bot']['token']
        self.target_channel = self.config['telegram_bot']['channel']

        # URL Processing Parameters
        self.url_params = self.config.get('url_params', {})
        self.affiliate_config = self.config.get('affiliate_config', {})

        # Facebook Configuration
        self.facebook_token = self.config['facebook']['access_token']
        self.facebook_page_id = self.config['facebook']['page_id']

        # Instagram Configuration
        self.instagram_username = self.config['instagram']['username']
        self.instagram_password = self.config['instagram']['password']

        # Logging Setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

        # State Management
        self.last_messages = self.load_last_messages()

        # Initialize Clients
        self.ig_client = Client()

    def load_last_messages(self):
        if os.path.exists('last_messages.json'):
            with open('last_messages.json', 'r') as file:
                return json.load(file)
        return {}

    def save_last_messages(self):
        with open('last_messages.json', 'w') as file:
            json.dump(self.last_messages, file)

    async def download_media(self, message):
        try:
            media_dir = os.path.join(os.getcwd(), 'temp_media')
            os.makedirs(media_dir, exist_ok=True)
            media_path = await message.download_media(file=media_dir)
            return media_path if media_path and os.path.exists(media_path) else None
        except Exception as e:
            self.logger.error(f"Media download error: {e}")
            return None

    def get_actual_url_with_selenium(self, redirect_url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(redirect_url, headers=headers, allow_redirects=True, timeout=30)
            return response.url
        except Exception as e:
            self.logger.error(f"URL Resolution Error: {e}")
            return redirect_url

    def process_url(self, url):
        # Add affiliate IDs based on the store configuration
        for store, config in self.affiliate_config.items():
            if store in url:
                parsed_url = urllib.parse.urlparse(url)
                query_params = dict(urllib.parse.parse_qsl(parsed_url.query))
                query_params.update(config['params'])
                url = urllib.parse.urlunparse(parsed_url._replace(
                    query=urllib.parse.urlencode(query_params)
                ))
        return url

    def shorten_url(self, long_url):
        try:
            response = requests.post(
                "http://152.67.30.229/shorten",
                json={"url": long_url}
            )
            print(response.json())
            return f"http://152.67.30.229{response.json()['short_url']}"
        except Exception as e:
            self.logger.error(f"URL Shortening Error: {e}")
            return long_url

    def process_links(self, text):
        url_regex = r'https?://\S+'
        urls = re.findall(url_regex, text)
        
        for url in urls:
            full_url = url if url.startswith('http') else f'https://{url}'
            resolved_url = self.get_actual_url_with_selenium(full_url)
            
            if resolved_url:
                processed_url = self.process_url(resolved_url)
                # Only shorten if it's Amazon or Flipkart
                parsed_url = urllib.parse.urlparse(processed_url)
                domain = parsed_url.netloc.replace('www.', '')
                print(f"Domain: {domain}")
                if domain.startswith(('amazon.', 'flipkart.')):
                    shortened_url = self.shorten_url(processed_url)
                    text = text.replace(url, shortened_url)
                else:
                    text = text.replace(url, processed_url)
        
        return text

    def send_telegram_message(self, message):
        # Find URLs in the message
        url_pattern = r'(http[s]?://\S+)'
        urls = re.findall(url_pattern, message)
        
        # Replace URLs with HTML formatted links
        formatted_message = message
        for url in urls:
            html_link = f'{url}'
            formatted_message = formatted_message.replace(url, html_link)
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {
            'chat_id': self.target_channel,
            'text': formatted_message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        return requests.post(url, params=params).json()


    def post_to_facebook(self, message, media_path=None):
        try:
            graph = facebook.GraphAPI(access_token=self.facebook_token)
            if media_path:
                with open(media_path, 'rb') as image:
                    graph.put_photo(image=image, message=message, album_path=f"{self.facebook_page_id}/photos")
            else:
                graph.put_object(parent_object=self.facebook_page_id, connection_name='feed', message=message)
            self.logger.info("Message posted to Facebook successfully")
        except Exception as e:
            self.logger.error(f"Facebook Posting Error: {e}")

    async def post_to_instagram(self, message, media_path):
        try:
            self.ig_client.login(self.instagram_username, self.instagram_password)
            self.ig_client.photo_upload(media_path, caption=message)
            self.logger.info("Successfully posted to Instagram")
        except Exception as e:
            self.logger.error(f"Instagram posting error: {e}")

    async def main(self):
        client = TelegramClient('session', self.api_id, self.api_hash)
        await client.start()

        while True:
            for channel in self.channels:
                try:
                    entity = await client.get_entity(channel)
                    messages = await client.get_messages(entity, limit=1)
                    if not messages:
                        continue
                    message = messages[0]
                    if self.last_messages.get(channel) == message.id:
                        continue

                    # Update last message ID
                    self.last_messages[channel] = message.id
                    self.save_last_messages()

                    # Process and forward the message
                    if message.text:
                        processed_text = self.process_links(message.text)
                        recent_messages = await client.get_messages(self.main_group, limit=10)
                        if all(msg.text != processed_text for msg in recent_messages if msg.text):
                            self.send_telegram_message(processed_text)
                            if isinstance(message.media, MessageMediaPhoto):
                                media_path = await self.download_media(message)
                                if media_path:
                                    self.post_to_facebook(processed_text, media_path)
                                    await self.post_to_instagram(processed_text, media_path)
                                    os.remove(media_path)
                            else:
                                self.post_to_facebook(processed_text)

                except Exception as e:
                    self.logger.error(f"Error processing channel {channel}: {e}")

            await asyncio.sleep(900)


if __name__ == '__main__':
    import sys
    bot = MultiChannelTelegramBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test post functionality
        # test_message = "**✨ Trending Styles For Men**⚡ Min. 40% off+ Extra 5% offView offer 👉 https://ajiio.in/HJQhHyn"
        test_message = "Mix Dry Fruits & Nuts, 1Kg at Rs.499 https://amzn.to/40YE268"
        processed_message = bot.process_links(test_message)
        # print(f"Processed message: {processed_message}")
        bot.send_telegram_message(processed_message)
        bot.post_to_facebook(processed_message)
        asyncio.run(bot.post_to_instagram(processed_message, None))
        print("Test posts sent to all platforms")
    else:
        # Normal continuous operation
        asyncio.run(bot.main())