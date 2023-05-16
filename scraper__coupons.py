import urllib.parse
from selectorlib import Extractor
import requests 
import json 
import argparse
import csv

#Comments
# Stores and Store links Combinatio added

#['https://www.amazon.in/gp/bestsellers/automotive/ref=zg_bs_nav_0', 'amazon-bs', 'selectors__yml/selectors__amazon.yml', 'amazon','https://www.amazon.in', 'amazon']
#[url, foldername, ymlfilepath, merchantname, baseurl, datasource]

xs = [
# ['https://www.amazon.in/gp/bestsellers/automotive/ref=zg_bs_nav_0', 'amazon-bs', 'selectors__yml/selectors__amazon.yml', 'amazon','https://www.amazon.in', 'amazon'],
['http://www.couponzguru.com/amazon/?utm_source=site&utm_medium=logo&utm_campaign=amazon', 'cgamazon', 'selectors__yml/selectors__coupons.yml', 'amazon','https://www.amazon.in', 'amazon'],
['http://www.desidime.com/stores/amazon-india', 'ddamazon', 'selectors__yml/selectors__desidime.yml', 'amazon','https://www.amazon.in', 'amazon'],
['http://www.couponzguru.com/shopping-coupon/flipkart/?utm_source=site&utm_medium=logo&utm_campaign=flipkart', 'cgflipkart', 'selectors__yml/selectors__coupons.yml', 'flipkart','https://www.flipkart.com', 'flipkart'],
['http://www.desidime.com/stores/flipkart', 'ddflipkart', 'selectors__yml/selectors__desidime.yml', 'flipkart','https://www.flipkart.com', 'flipkart']
]

argparser = argparse.ArgumentParser()

# Loop all xs array 
for str, x in enumerate(xs):
    # url = input ("Enter url :")
    url = x[0]
    # store = input ("Enter Store :")
    store = x[1]
    # argparser.add_argument(url, help='Store URL')
    merchant = x[3]

    data__source = x[5]

    # Create an Extractor by reading from the YAML file
    e = Extractor.from_yaml_file(x[2])

    #can be moved out
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    headers = {'User-Agent': user_agent}

    # Download the page using requests
    args = argparser.parse_args()
    r = requests.get(url, headers=headers)
    # Pass the HTML of the page and create 
    data = e.extract(r.text)
    # Print the data 
    # print(json.dumps(data, indent=True))
    # with open('api.json', 'w') as outfile:
    #     json.dump(data, outfile)    



    # with open('api.json') as json_file: 
    #     getdata = json.load(json_file) 
        
    #     temp = getdata['electronic'] 
    
    #     # python object to be appended 
    #     y = data['electronic']
    #     temp += y  
    
        # appending data to emp_details  

    #dump data to store api files        
    with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
        json.dump(data, outfile)    

    #get data from store api files and santise links  
    with open('stores/'+store+'/api__coupons.json') as json_file: 
        getdata = json.load(json_file) 
    for x in getdata['products']:
        x['merchant'] = merchant
        if x['link'] :

                # if data__source == 'amazon':
                #     x['link'] = 'https://www.amazon.in' + x['link']
                # print(requests.head(x['link']).headers['location'])
                # x['link'] = requests.head(x['link']).headers['location']
                if  requests.head(x['link']) :
                    if  requests.head(x['link']).headers['Location'] :
                        x['link'] = requests.head(x['link']).headers['Location']
                        print("true")
                else : 
                    x['link'] = x['link']

    with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
        json.dump(getdata['products'], outfile)    

    print("First Time Data Sanitized")


    # with open('stores/'+store+'/api__coupons.json') as json_file: 
    #     getdata = json.load(json_file)     
    # for x in getdata:
    #     if x['link'] :
    #             # print( x['link'])
    #             # print(requests.head(x['link']).headers)
    #             if  requests.head(x['link']) :
    #                 if  requests.head(x['link']).headers['Location'] :
    #                     x['link'] = requests.head(x['link']).headers['Location']
    #                     print("true")
    #             else : 
    #                   x['link'] = x['link']

    # with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
    #     json.dump(getdata, outfile)    

    # print("Second Time Data Sanitized")

    #csv  not working
    # fieldnames = ['name', 'description', 'link']
    # with open('api__coupons.csv', 'w', encoding='UTF8', newline='') as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(getdata)    

    #get data from store api files and santise links and append affiliate ids
    with open('stores/'+store+'/api__coupons.json') as json_file: 
        getdata = json.load(json_file)     
    for x in getdata:
        if x['link'] :
                # print( x['link'])
                # print(requests.head(x['link']).headers)
                if  x['link'] :
                    url = x['link']
                    params = {'tag':'offerscodes-21', 'affid': 'vishwajit8'}

                    url_parts = list(urllib.parse.urlparse(url))
                    query = dict(urllib.parse.parse_qsl(url_parts[4]))
                    query.update(params)

                    url_parts[4] = urllib.parse.urlencode(query)

                    print(urllib.parse.urlunparse(url_parts))
                    x['link'] = urllib.parse.urlunparse(url_parts)

    with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
        json.dump(getdata, outfile)    
