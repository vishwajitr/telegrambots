from flask import Flask, request, jsonify
import json

app = Flask(__name__)


# Load JSON files
file1 = "./stores/cgamazon/api__coupons.json"
file2 = "./stores/cgflipkart/api__coupons.json"
file3 = "./stores/ddamazon/api__coupons.json"
file4 = "./stores/ddflipkart/api__coupons.json"

# Define API endpoint
@app.route('/search', methods=['GET'])
def search_results():
    keyword = request.args.get('keyword')

    # Perform search in each JSON file
    results = []
    for file in [file1, file2, file3, file4]:
        with open(file, 'r') as f:
            data = json.load(f)
            for item in data:
                if 'merchant' in item and item['merchant'] == keyword:
                    results.append(item)

    return jsonify({'results':results})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
