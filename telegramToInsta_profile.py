import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import configparser

class TelegramInstagramSync:
    def __init__(self):
        # Telegram configurations - directly specify your credentials
        self.telegram_api_id = "22544328"
        self.telegram_api_hash = "c9b5f81a263933e3fecce08cc719fa00"
        self.telegram_bot_token = "6831241416:AAEamtwesUyXH5NBAGt3gLzMBsabgahGL9o"

        # Instagram configurations
        self.ig_username = "vishwajit.rikame"
        self.ig_password = "vishu@1990"

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
            self.ig_client.login(self.ig_username, self.ig_password)
            self.logger.info(f"Instagram login successful for user: {self.ig_username}")
        except LoginRequired as e:
            self.logger.error(f"Instagram login failed with error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during Instagram login: {str(e)}")
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
            caption = event.message.text or ""
            caption = caption[:2200] if len(caption) > 2200 else caption

            if isinstance(event.message.media, MessageMediaPhoto):
                media_path = await self.download_media(event.message)
                
                if media_path:
                    try:
                        from PIL import Image
                        img = Image.open(media_path)
                        img.verify()
                        
                        upload_result = self.ig_client.photo_upload(
                            path=media_path,
                            caption=caption
                        )
                        self.logger.info(f"Successfully uploaded post: {upload_result.pk}")
                        os.remove(media_path)
                    except Exception as e:
                        self.logger.error(f"Instagram upload failed: {e}")
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

    async def test_connection(self):
        try:
            user_info = self.ig_client.account_info()
            self.logger.info(f"Instagram connected: {user_info.username}")
            
            me = await self.telegram_client.get_me()
            self.logger.info(f"Telegram connected: {me.username}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False

    async def start_sync(self, source_channel):
        await self.telegram_client.start(bot_token=self.telegram_bot_token)
        await self.login_instagram()
        await self.test_connection()

        @self.telegram_client.on(events.NewMessage(chats=source_channel))
        async def handler(event):
            await self.process_telegram_message(event)

        await self.telegram_client.run_until_disconnected()

def main():
    sync = TelegramInstagramSync()
    asyncio.run(sync.start_sync('@dealstodayindia001'))

if __name__ == '__main__':
    main()
