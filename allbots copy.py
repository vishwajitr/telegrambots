import os
import asyncio
import logging
import yaml
import re
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
import urllib.parse
import requests
from selenium import webdriver
import facebook
import schedule
import time
from instagrapi import Client

class MultiChannelTelegramBot:
    def __init__(self, config_path='config.yaml'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Telegram Configuration
        self.api_id = self.config['telegram']['api_id']
        self.api_hash = self.config['telegram']['api_hash']
        self.phone_number = self.config['telegram']['phone_number']
        self.channels = self.config['telegram']['channels']
        
        # Bot Configuration
        self.bot_token = self.config['telegram_bot']['token']
        self.target_channel = self.config['telegram_bot']['channel']
        
        # URL Processing Parameters
        self.url_params = self.config.get('url_params', {})
        
        # Bitly Configuration
        self.bitly_token = self.config['bitly']['access_token']
        
        # Facebook Configuration
        self.facebook_token = self.config['facebook']['access_token']
        self.facebook_page_id = self.config['facebook']['page_id']
        
        # Instagram Configuration
        self.instagram_username = self.config['instagram']['username']
        self.instagram_password = self.config['instagram']['password']
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients
        self.ig_client = Client()

    async def download_media(self, message):
        try:
            media_dir = os.path.join(os.getcwd(), 'temp_media')
            os.makedirs(media_dir, exist_ok=True)
            media_path = await message.download_media(file=media_dir)
            
            if media_path and os.path.exists(media_path):
                file_size = os.path.getsize(media_path)
                self.logger.info(f"Media downloaded successfully: {media_path} (Size: {file_size} bytes)")
                return media_path
            return None
        except Exception as e:
            self.logger.error(f"Media download error: {e}")
            return None
        
    def get_actual_url_with_selenium(self, redirect_url):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            driver.get(redirect_url)
            actual_url = driver.current_url
            driver.quit()
            return actual_url
        except Exception as e:
            self.logger.error(f"Selenium URL Error: {e}")
            return None

    def process_url(self, url):
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(self.url_params)
        url_parts[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(url_parts)

    def shorten_url(self, long_url):
        bitly_api_url = 'https://api-ssl.bitly.com/v4/shorten'
        headers = {
            'Authorization': f'Bearer {self.bitly_token}',
            'Content-Type': 'application/json',
        }
        data = {'long_url': long_url}
        
        try:
            response = requests.post(bitly_api_url, headers=headers, json=data)
            return response.json()['link'] if response.status_code == 200 else None
        except Exception as e:
            self.logger.error(f"URL Shortening Error: {e}")
            return None

    def process_links(self, text):
        url_regex = r'https?://\S+'
        urls = re.findall(url_regex, text)

        for url in urls:
            new_link = self.get_actual_url_with_selenium(url)
            if new_link:
                processed_url = self.process_url(new_link)
                shortened_url = self.shorten_url(processed_url)
                if shortened_url:
                    text = text.replace(url, shortened_url)
        return text

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {
            'chat_id': self.target_channel,
            'text': message,
            'parse_mode': 'HTML'
        }
        return requests.post(url, params=params).json()

    def post_to_facebook(self, message):
        try:
            graph = facebook.GraphAPI(access_token=self.facebook_token)
            graph.put_object(parent_object=self.facebook_page_id, 
                           connection_name='feed', 
                           message=message)
            self.logger.info("Message posted to Facebook successfully")
        except Exception as e:
            self.logger.error(f"Facebook Posting Error: {e}")

    async def post_to_instagram(self, message, media_path):
        try:
            self.ig_client.login(self.instagram_username, self.instagram_password)
            caption = message[:2200] if len(message) > 2200 else message
            
            from PIL import Image
            img = Image.open(media_path)
            img.verify()
            
            upload_result = self.ig_client.photo_upload(
                path=media_path,
                caption=caption
            )
            self.logger.info(f"Successfully uploaded post to Instagram")
            return True
        except Exception as e:
            self.logger.error(f"Instagram posting error: {e}")
            return False

    async def main(self):
      client = TelegramClient('session', self.api_id, self.api_hash)
      await client.start()
      
      while True:
          for channel in self.channels:
              try:
                  entity = await client.get_entity(channel)
                  messages = await client.get_messages(entity, limit=1)
                  
                  for message in messages:
                      if message.text:
                          processed_text = self.process_links(message.text)
                          self.send_telegram_message(processed_text)
                          
                          if isinstance(message.media, MessageMediaPhoto):
                              media_path = await self.download_media(message)
                              if media_path:
                                  try:
                                      # Post to Facebook with media
                                      graph = facebook.GraphAPI(access_token=self.facebook_token)
                                      with open(media_path, 'rb') as image:
                                          graph.put_photo(
                                              image=image,
                                              message=processed_text,
                                              album_path=f"{self.facebook_page_id}/photos"
                                          )
                                      self.logger.info("Posted to Facebook with media successfully")
                                      
                                      # Post to Instagram
                                      await self.post_to_instagram(processed_text, media_path)
                                  finally:
                                      if os.path.exists(media_path):
                                          os.remove(media_path)
                                          self.logger.info(f"Cleaned up media file: {media_path}")
                          else:
                              # Text-only post to Facebook
                              self.post_to_facebook(processed_text)
                              
              except Exception as e:
                  self.logger.error(f"Message Fetching Error for {channel}: {e}")
                      
              await asyncio.sleep(900)


def run_bot():
    bot = MultiChannelTelegramBot()
    asyncio.run(bot.main())

if __name__ == '__main__':
    run_bot()
