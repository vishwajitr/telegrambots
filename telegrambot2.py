# Telegram https://web.telegram.org/k/#@dealstodayindia001 to https://www.instagram.com/trendingoffers5 [media based post upload]

import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

class TelegramInstagramSync:
    def __init__(self, primary_username, primary_password, target_username):
        # Telegram configurations
        self.telegram_api_id = "22544328"
        self.telegram_api_hash = "c9b5f81a263933e3fecce08cc719fa00"
        self.telegram_bot_token = "6831241416:AAEamtwesUyXH5NBAGt3gLzMBsabgahGL9o"

        # Instagram configurations
        self.primary_username = primary_username
        self.primary_password = primary_password
        self.target_username = target_username

        # Initialize clients
        self.telegram_client = TelegramClient('session', 
                                            self.telegram_api_id, 
                                            self.telegram_api_hash)
        self.ig_client = Client()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def login_instagram(self):
        try:
            # Login to primary account first
            self.ig_client.login(self.primary_username, self.primary_password)
            
            # Get target account ID
            target_user_id = self.ig_client.user_id_from_username(self.target_username)
            
            self.logger.info(f"Preparing to post on account: {self.target_username}")
            
            return target_user_id
        except Exception as e:
            self.logger.error(f"Instagram login/account lookup failed: {str(e)}")
            raise

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

    async def process_telegram_message(self, event):
        try:
            # Get target user ID
            target_user_id = await self.login_instagram()
            
            caption = event.message.text or ""
            caption = caption[:2200] if len(caption) > 2200 else caption

            if isinstance(event.message.media, MessageMediaPhoto):
                media_path = await self.download_media(event.message)
                
                if media_path:
                    try:
                        from PIL import Image
                        img = Image.open(media_path)
                        img.verify()
                        
                        # Direct upload to target account
                        upload_result = self.ig_client.photo_upload(
                            path=media_path,
                            caption=caption
                        )
                        self.logger.info(f"Successfully uploaded post to {self.target_username}: {upload_result.pk}")
                        os.remove(media_path)
                    except Exception as e:
                        self.logger.error(f"Instagram upload failed: {e}")
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

    async def start_sync(self, source_channel):
        await self.telegram_client.start(bot_token=self.telegram_bot_token)
        
        @self.telegram_client.on(events.NewMessage(chats=source_channel))
        async def handler(event):
            await self.process_telegram_message(event)

        await self.telegram_client.run_until_disconnected()

def main():
    sync = TelegramInstagramSync(
        primary_username='trendingoffers5', 
        primary_password='vishu@1992', 
        target_username='trendingoffers5'
    )
    asyncio.run(sync.start_sync('@dealstodayindia001'))

if __name__ == '__main__':
    main()