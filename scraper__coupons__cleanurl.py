from selectorlib import Extractor
import requests 
import json 
import argparse
import csv

argparser = argparse.ArgumentParser()
store = input ("Enter Store :")
# argparser.add_argument(url, help='Store URL')

with open('stores/'+store+'/api__coupons.json') as json_file: 
    getdata = json.load(json_file)     
for x in getdata:
    if x['link'] :
            # print( x['link'])
            # print(requests.head(x['link']).headers)
            if  requests.head(x['link']) :
                print(requests.head(x['link']).headers['Location'])
                if  (x['link'] != requests.head(x['link']).headers['Location']) :
                    x['link'] = requests.head(x['link']).headers['Location']
                    print("true")
                else : x['link'] = x['link']  
            else : 
                  x['link'] = x['link']

with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
    json.dump(getdata, outfile)    

exec(open("scraper__coupons__cleanurl.py").read())