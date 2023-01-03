from selectorlib import Extractor
import requests 
import json 
import argparse
import csv

argparser = argparse.ArgumentParser()
url = input ("Enter url :")
store = input ("Enter Store :")
# argparser.add_argument(url, help='Store URL')

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors__coupons.yml')

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
         
with open('stores/'+store+'/api__coupons.json', 'w') as outfile:
    json.dump(data, outfile)    


with open('stores/'+store+'/api__coupons.json') as json_file: 
    getdata = json.load(json_file) 
for x in getdata['products']:
    x['merchant'] = store
    if x['link'] :
            # print( x['link'])
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

exec(open("aff__tag__replacer.py").read())