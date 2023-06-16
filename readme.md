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