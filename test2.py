from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start maximized
chrome_options.add_argument("--disable-infobars")  # Disable info bars
chrome_options.add_argument("--disable-extensions")  # Disable extensions

# Path to your ChromeDriver
webdriver_service = Service('/path/to/chromedriver')  # Update this path

def process_users():
    # Load user data
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    print(f"Loaded {len(users)} users from JSON file")
    
    # Create log file
    log_file = f'usernames_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    for index, user in enumerate(users, 1):
        peer_id = user['peerId']
        current_name = user['name']
        
        # Generate Telegram web URL
        web_url = f"https://web.telegram.org/k/#{peer_id}"
        
        print(f"\n[{index}/{len(users)}]")
        print(f"Opening: {current_name} (ID: {peer_id})")
        
        # Open link in browser
        driver.get(web_url)
        time.sleep(5)  # Wait for the page to load

        # Try to find the username in the sidebar
        try:
            # Wait for the username to be visible
            username_element = driver.find_element(By.XPATH, "//div[@class='tgme_username']")
            username = username_element.text.strip()
            print(f"✅ Found username: @{username}")

            # Log the information
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"PeerID: {peer_id}\n")
                f.write(f"Name: {current_name}\n")
                f.write(f"Username: @{username}\n")
                f.write("-" * 30 + "\n")
        except Exception as e:
            print(f"❌ Could not find username for {current_name}: {str(e)}")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"PeerID: {peer_id}\n")
                f.write(f"Name: {current_name}\n")
                f.write(f"Username: SKIPPED\n")
                f.write("-" * 30 + "\n")

        # Small delay before next user
        time.sleep(2)

    print(f"\nCompleted! Check {log_file} for usernames.")
    driver.quit()  # Close the browser

if __name__ == '__main__':
    print("Starting the program...")
    process_users()