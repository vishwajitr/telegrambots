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
        self.facebook_token = self.config['facebook']['page_token']
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
        """
        Process any URL to add affiliate parameters and handle various URL formats
        """
        try:
            self.logger.info(f"Processing URL: {url}")
            
            url = url.strip()
            # Basic URL validation and formatting
            if not url:
                return url
                
            if not url.startswith(('http://', 'https://')):
                if url.startswith('//'):
                    url = f"https:{url}"
                else:
                    url = f"https://{url}"
            
            url_shorteners = ['blinks.to', 'fkrt.cc', 'ajiio.in', 'amzn.to']
            
            # Resolve shortened URLs
            if any(shortener in url for shortener in url_shorteners):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                    response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
                    if response.status_code == 200:
                        url = response.url
                        self.logger.info(f"URL resolved to: {url}")
                except Exception as e:
                    self.logger.error(f"Error resolving shortened URL {url}: {e}")
            
            # Parse and process URL
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower().replace('www.', '')
            
            # Extract existing query parameters
            query_params = dict(urllib.parse.parse_qsl(parsed_url.query))
            # Process Amazon and Flipkart URLs
            if domain in ['amazon.in', 'amazon.com', 'flipkart.com']:
                if 'amazon' in domain:
                    store = 'amazon'
                elif 'flipkart' in domain:
                    store = 'flipkart'
                # self.logger.info(f"Processing {store} URL: {domain}")
                # # Add debug logging for configuration
                # self.logger.info(f"Available affiliate configs: {self.affiliate_config.keys()}")
                # self.logger.info(f"Current store: {store}")
                
                if store in self.affiliate_config:
                    self.logger.info(f"Found affiliate config for {store}: {self.affiliate_config[store]}")

                    
                    # Add affiliate parameters directly without filtering
                    store_params = self.affiliate_config[store].get('params', {})
                    query_params.update(store_params)  # Add affiliate params to existing params
                    
                    processed_url = urllib.parse.urlunparse(
                        parsed_url._replace(
                            query=urllib.parse.urlencode(query_params),
                            fragment=''
                        )
                    )
                    self.logger.info(f"Processed URL: {processed_url}")
                    return processed_url
                else:
                    self.logger.info(f"No affiliate config found for {store}")
                    return url
            
            # Use Cuelinks for all other URLs
            elif 'cuelinks' in self.affiliate_config:
                print("cuelinks")  # Debug print
                # Preserve original important parameters
                important_params = ['utm_source', 'utm_medium', 'utm_campaign']
                filtered_params = {
                    k: v for k, v in query_params.items() 
                    if k in important_params
                }
                
                # Add Cuelinks parameters
                cuelinks_params = self.affiliate_config['cuelinks'].get('params', {})
                filtered_params.update(cuelinks_params)
                
                processed_url = urllib.parse.urlunparse(
                    parsed_url._replace(
                        query=urllib.parse.urlencode(filtered_params),
                        fragment=''
                    )
                )
                self.logger.info(f"Processed URL: {processed_url}")
                return processed_url
            
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
            return url

    
    def process_links(self, text):
        if any(x in text.lower() for x in ["t.me/", "telegram.me/", "/telegram"]):
            return None        
        url_regex = r'(?:https?:\/\/)?(?:www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\/[^\s]*)?'
        urls = re.findall(url_regex, text)
        
        self.logger.info(f"Found URLs: {urls}")
        
        for url in urls:
            full_url = url if url.startswith('http') else f'https://{url}'
            processed_url = self.process_url(full_url)
            
            if processed_url != full_url:  # Only shorten if URL was processed
                shortened_url = self.shorten_url(processed_url)
                self.logger.info(f"Shortened to: {shortened_url}")
                text = text.replace(url, shortened_url)
        
        return text

    def shorten_url(self, long_url):
            try:
                response = requests.post(
                    "http://152.67.30.229/shorten",
                    json={"url": long_url}
                )
                # print(response.json())
                return f"http://152.67.30.229{response.json()['short_url']}"
            except Exception as e:
                self.logger.error(f"URL Shortening Error: {e}")
                return long_url


    def send_telegram_message(self, message):
        try:
            # Ensure message is a string
            message_text = str(message)
            
            # Find URLs in the message
            url_pattern = r'(http[s]?://\S+)'
            urls = re.findall(url_pattern, message_text)
            self.logger.info(f"Found URLs: {urls}")
            
            # Replace URLs with HTML formatted links
            formatted_message = message_text
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
            response = requests.post(url, params=params).json()
            self.logger.info(f"Telegram API response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error in send_telegram_message: {e}")
            return None


    def process_facebook_url(self, url):
        """
        Process a URL for Facebook posts to ensure proper attribution for affiliate links.
        """
        try:
            self.logger.info(f"Processing URL: {url}")
            
            url = url.strip()
            # Basic URL validation and formatting
            if not url:
                return url
                
            if not url.startswith(('http://', 'https://')):
                if url.startswith('//'):
                    url = f"https:{url}"
                else:
                    url = f"https://{url}"
            
            url_shorteners = ['blinks.to', 'fkrt.cc', 'ajiio.in', 'amzn.to']
            
            # Resolve shortened URLs
            if any(shortener in url for shortener in url_shorteners):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                    response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
                    if response.status_code == 200:
                        url = response.url
                        self.logger.info(f"URL resolved to: {url}")
                except Exception as e:
                    self.logger.error(f"Error resolving shortened URL {url}: {e}")
            
            # Parse and process URL
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower().replace('www.', '')
            
            # Extract existing query parameters
            query_params = dict(urllib.parse.parse_qsl(parsed_url.query))
            # Process Amazon and Flipkart URLs
            
            if domain not in ['amazon.in', 'amazon.com', 'flipkart.com']:
                # Add Cuelinks parameters if available
                if 'cuelinks' in self.affiliate_config:
                    important_params = ['utm_source', 'utm_medium', 'utm_campaign']
                    filtered_params = {
                        k: v for k, v in query_params.items() 
                        if k in important_params
                    }

                    cuelinks_params = self.affiliate_config['cuelinks'].get('fb_params', {})
                    filtered_params.update(cuelinks_params)
                
                # Construct the processed URL
                processed_url = urllib.parse.urlunparse(
                    parsed_url._replace(
                        query=urllib.parse.urlencode(filtered_params),
                        fragment=''
                    )
                )
            
            self.logger.info(f"Processed Facebook URL: {processed_url}")
            return processed_url

        except Exception as e:
            self.logger.error(f"Error processing Facebook URL {url}: {e}")
            return url

    def post_to_facebook(self, message, media_path=None):
        try:
            processed_message = self.process_facebook_url(message)
            print(f"111: {processed_message}")
            graph = facebook.GraphAPI(access_token=self.facebook_token)
            if media_path:
                with open(media_path, 'rb') as image:
                    graph.put_photo(image=image, message=processed_message, album_path=f"{self.facebook_page_id}/photos")
            else:
                graph.put_object(parent_object=self.facebook_page_id, connection_name='feed', message=processed_message)
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
                        if processed_text is None:  # Skip messages with Telegram URLs
                            continue
                            
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
        test_message = "**✨ Trending Styles For Men**⚡ Min. 40% off+ Extra 5% offView offer 👉 https://www.ajio.com/s/40-to-80-percent-off-5399-784712"
        # test_message = "Safari Laptop Backpack Starts at Rs.445. https://fkrt.cc/EDRTbr"
        # test_message = "**Myntra**: Aristocrat hard trolleys starting @1499 https://linkredirect.in/visitretailer/2111?id=1962507&shareid=UbJui72&dl=https%3A%2F%2Fwww.myntra.com%2Faristocrat-trolley%3Ff%3DBag%2520Type%253ASuitcase%26rawQuery%3DAristocrat%2520Trolley%26rf%3FPrice%253A1400.0_28100.0_1400.0%2520TO%252028100.0%26sort%3Dprice_asc"
        # test_message = "**💖 Get Date-Ready This Valentine's! 💖 **🔥 Bestselling Trimmers, Hairdryers, Straighteners & More for a Perfect Look! ✨ Up to 60% Off | 🚚 Top Brands, Fast Delivery 👉 blinks.to/oJGc604"
        processed_message = bot.process_facebook_url(test_message)
        # print(f"Processed message: {processed_message}")
        # bot.send_telegram_message(processed_message)
        bot.post_to_facebook(processed_message)
        asyncio.run(bot.post_to_instagram(processed_message, None))
        print("Test posts sent to all platforms")
    else:
        # Normal continuous operation
        asyncio.run(bot.main())