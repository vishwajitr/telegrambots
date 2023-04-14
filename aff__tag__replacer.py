import urllib.parse
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



