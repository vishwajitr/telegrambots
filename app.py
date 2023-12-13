from flask import Flask, request, jsonify
import json
import os
import glob
from flask_cors import CORS
import logging
import traceback


app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

# Allowing specific headers and methods
CORS(app, headers=['Content-Type'], methods=['GET'])

logging.basicConfig(filename='execution_log.log', level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s - Line %(lineno)d')

xs = [
['http://www.couponzguru.com/amazon/?utm_source=site&utm_medium=logo&utm_campaign=amazon', 'cgamazon', 'selectors__yml/selectors__coupons.yml', 'amazon','https://www.amazon.in', 'amazon'],
['http://www.desidime.com/stores/amazon-india', 'ddamazon', 'selectors__yml/selectors__desidime.yml', 'amazon','https://www.amazon.in', 'amazon'],
['http://www.couponzguru.com/shopping-coupon/flipkart/?utm_source=site&utm_medium=logo&utm_campaign=flipkart', 'cgflipkart', 'selectors__yml/selectors__coupons.yml', 'flipkart','https://www.flipkart.com', 'flipkart'],
['http://www.desidime.com/stores/flipkart', 'ddflipkart', 'selectors__yml/selectors__desidime.yml', 'flipkart','https://www.flipkart.com', 'flipkart']
]

# Load JSON files
file1 = "./stores/cgamazon/api__coupons.json"
file2 = "./stores/cgflipkart/api__coupons.json"
file3 = "./stores/ddamazon/api__coupons.json"
file4 = "./stores/ddflipkart/api__coupons.json"

@app.route('/', methods=['GET'])
def hello_world():
    return '<h1>Hello World from Flask!</ h1>'

@app.route('/offers', methods=['GET'])
def offers():
    offers_data = []

    # Get all JSON files in stores/*/ folders
    folder_paths = glob.glob('./stores/*/')
    for folder_path in folder_paths:
        json_files = glob.glob(os.path.join(folder_path, '*.json'))
        for json_file in json_files:
            if os.path.getsize(json_file) > 0:
                with open(json_file, 'r') as file:
                    json_data = json.load(file)
                    offers_data.append(json_data)
            else:
                offers_data = offers_data
    # Return the offers data as a JSON response
    return jsonify(offers_data[0])

# Define API endpoint
@app.route('/search/offer__by__store__slug', methods=['GET'])
def offer__by__store__slug():
    keyword = request.args.get('q')
    
    # Perform search in each JSON file
    results = []
    for file in [file1, file2, file3, file4]:
        if os.path.getsize(file) > 0:
            with open(file, 'r') as f:
                data = json.load(f)
                for item in data:
                    if 'merchant' in item and item['merchant'] == keyword:
                        results.append(item)
        else:
            results = results
    return jsonify({'results':results})

# Define API endpoint
@app.route('/search/offers__by__query', methods=['GET'])
def offers__by__query():
    keyword = request.args.get('q')
    # Perform search in each JSON file
    results = []
    for file in [file1, file2, file3, file4]:
        if os.path.getsize(file) > 0:
            with open(file, 'r') as f:
                data = json.load(f)
                for item in data:
                    if 'merchant' in item and item['merchant'] == keyword:
                        results.append(item)
                    else:
                        results = results    

    return jsonify({'results':results})
   


@app.route('/search/prod__by__slug', methods=['GET'])
def prod__by__slug():
    query = request.args.get('q')  # Get the value of the 'q' parameter

    results = []
    products_data = []
    for file in [file1, file2, file3, file4]:
        with open(file, 'r') as f:
            products_data.extend(json.load(f))

            # Filter the products based on a partial match of the slug with the query (case-insensitive)
    filtered_products = [product for product in products_data if query.lower() in product['slug'].lower()]

    return jsonify(filtered_products)
  

@app.route('/search/store__by__slug', methods=['GET'])
def search_by_slug():
    try:
        q = request.args.get('q')  # Get the value of the 'q' parameter

        # Load the directStores data from the JSON file
        with open('./stores__data/directStores.json', 'r') as file:
            direct_stores = json.load(file)

        # Filter the direct_stores based on the slug (q)
        filtered_stores = [store for store in direct_stores if store['slug'] == q]

        # Return the filtered stores as a JSON response
        return jsonify(filtered_stores)
    except Exception as e:
            # Log the exception details
            logging.exception("An error occurred in the /search/store__by__slug endpoint")
            return jsonify([{}])

@app.route('/search/stores__by__query', methods=['GET'])
def stores__by__query():
    try:
        q = request.args.get('q')  # Get the value of the 'q' parameter

        # Load the directStores data from the JSON file
        with open('./stores__data/directStores.json', 'r') as file:
            direct_stores = json.load(file)

        # Filter the direct_stores based on the partial slug match (q)
        filtered_stores = [store for store in direct_stores if q.lower() in store['slug'].lower()]

        # Return the filtered stores as a JSON response
        return jsonify(filtered_stores)
    except Exception as e:
            # Log the exception details
            logging.exception("An error occurred in the /search/stores__by__query endpoint")
            return jsonify([{}])

@app.route('/stores', methods=['GET'])
def get_all_stores():
    file_path = './stores__data/directStores.json'

    with open(file_path, 'r') as file:
        stores_data = json.load(file)

    return jsonify(stores_data)

@app.route('/keywords', methods=['GET'])
def get_keywords():
    file_path = './keyword__data/kwsData.json'

    with open(file_path, 'r') as file:
        keywords_data = json.load(file)

    return jsonify(keywords_data)

@app.route('/kws__by__slug', methods=['GET'])
def get_keyword_by_slug():
    query = request.args.get('q')  # Get the value of the 'q' parameter

    file_path = './keyword__data/kwsData.json'

    with open(file_path, 'r') as file:
        keywords_data = json.load(file)

    # Filter the keywords based on the matching keyword_slug (case-insensitive)
    filtered_keywords = [keyword for keyword in keywords_data if query.lower() in keyword['keyword_slug'].lower()]

    return jsonify(filtered_keywords)

@app.route('/kws__by__query', methods=['GET'])
def get_keywords_by_query():
    query = request.args.get('q')  # Get the value of the 'q' parameter

    file_path = 'keyword__data/kwsData.json'

    with open(file_path, 'r') as file:
        keywords_data = json.load(file)

    # Filter the keywords based on a partial match of the query with the keyword (case-insensitive)
    filtered_keywords = [keyword for keyword in keywords_data if query.lower() in keyword['keyword'].lower()]

    return jsonify(filtered_keywords)

@app.errorhandler(500)
def handle_500_error(e):
    # Log the error details
    logging.error("An internal server error occurred: %s", str(e))
    logging.error("Traceback: %s", traceback.format_exc())

    # Return a custom JSON response or just a generic error messages
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port='5001')
