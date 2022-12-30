import yaml, json

with open('data.yaml') as f:
    print(json.dumps(yaml.load(f)))