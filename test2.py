from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def scrape_telegram_user_data(channel_username):
    chrome_options = Options()
    # Comment out headless to debug visually
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')  # Ensures proper rendering
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Bypass detection
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")


    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        channel_url = f"https://t.me/s/{channel_username.replace('@', '')}"
        driver.get(channel_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        
        # Scroll to load content
        driver = webdriver.Chrome(options=chrome_options)
        # time.sleep(2)  # Allow lazy-loaded content to appear

        # Scraping user data
        user_data = {
            'channel_name': wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_channel_info_header_title"))).text,
            'subscribers': wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_channel_info_counter_value"))).text,
            'description': driver.find_element(By.CLASS_NAME, "tgme_channel_info_description").text if driver.find_elements(By.CLASS_NAME, "tgme_channel_info_description") else "No description available",
            'photo_url': driver.find_element(By.CLASS_NAME, "tgme_page_photo_image").get_attribute("src") if driver.find_elements(By.CLASS_NAME, "tgme_page_photo_image") else "No photo available"
        }
        print(user_data)

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error fetching data: {e}")
        user_data = {}

    finally:
        driver.quit()

    return user_data

# Example usage
channel_username = "offers_flipkart"
user_info = scrape_telegram_user_data(channel_username)

if user_info:
    print("Channel Info:")
    print(f"Name: {user_info.get('channel_name', 'N/A')}")
    print(f"Subscribers: {user_info.get('subscribers', 'N/A')}")
    print(f"Description: {user_info.get('description', 'N/A')}")
    print(f"Profile Photo URL: {user_info.get('photo_url', 'N/A')}")
else:
    print("Failed to retrieve channel information.")
