https://jsoneditoronline.org/#left=local.nilece&right=local.gekela
https://www.geeksforgeeks.org/amazon-product-price-tracker-using-python/

to install
pip3 install requests selectorlib

python test.py
python scraper.py https://www.amazon.in/gp/bestsellers/automotive/ref=zg_bs_nav_0




1. 
python scraper__coupons.py

store urls:https://www.couponzguru.com/shopping-coupon/flipkart/?utm_source=site&utm_medium=logo&utm_campaign=flipkart
2. to change shorten url to actual urls 
python scraper__coupons__cleanurl.py




Sheet Link - Get
Open link of store
Get Data
Compare if title rpeats if yes remove from current Data
Save that sheet with Date Name




Amazon Test 

electronic:
    css: li.zg-item-immersion
    multiple: true
    type: Text
    children:
        product_link:
            css: .a-link-normal
            type: Link
        product_title:
            css: .p13n-sc-truncated
            type: Text
        product_image_url:
            css: img
            type: Attribute
            attribute: src
            
scp -r crawler/ OffersApp3:/home/ubuntu

server to local file download
scp OffersApp3:/home/ubuntu/crawler/app.py crawler/
scp OffersApp3:/home/ubuntu/crawler/stores/cgamazon/api__coupons.json crawler/stores/cgamazon/api__coupons.json 


scp crawler/app.py OffersApp3:/home/ubuntu/crawler/app.py
scp crawler/scraper__coupons.py OffersApp3:/home/ubuntu/crawler/scraper__coupons.py

scp crawler/stores/cgamazon/api__coupons.json OffersApp3:/home/ubuntu/crawler/stores/cgamazon/api__coupons.json


pipreqs
pip install -r requirements.txt
nohup python3 app.py &

ps aux | grep app.py
kill <processid>


http://140.238.244.200/offers
http://140.238.244.200/search/offers__by__query?q=amazon
http://140.238.244.200/search/offer__by__store__slug?q=amazon
http://140.238.244.200/search/prod__by__slug?q=amazon
http://140.238.244.200/search/store__by__slug?q=amazon
http://140.238.244.200/search/stores__by__query?q=am
http://140.238.244.200/stores
http://140.238.244.200/keywords
http://140.238.244.200/kws__by__slug?q=myntra
http://140.238.244.200/kws__by__query?q=myn



http://127.0.0.1:5001/offers
http://127.0.0.1:5001/search/offers__by__query?q=amazon
http://127.0.0.1:5001/search/offer__by__store__slug?q=amazon
http://127.0.0.1:5001/search/prod__by__slug?q=amazon
http://127.0.0.1:5001/search/store__by__slug?q=amazon
http://127.0.0.1:5001/search/stores__by__query?q=am
http://127.0.0.1:5001/stores
http://127.0.0.1:5001/keywords
http://127.0.0.1:5001/kws__by__slug?q=myntra
http://127.0.0.1:5001/kws__by__query?q=myn


sudo service cron reload