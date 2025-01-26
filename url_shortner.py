from fastapi import FastAPI, HTTPException
import string
import random
import uvicorn
from pydantic import BaseModel
import json

app = FastAPI()

def load_mappings():
    try:
        with open('url_mappings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_mappings():
    with open('url_mappings.json', 'w') as f:
        json.dump(url_mapping, f)

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class URL(BaseModel):
    url: str

url_mapping = load_mappings()

@app.post("/shorten")
def shorten_url(url_data: URL):
    short_id = generate_short_id()
    url_mapping[short_id] = url_data.url
    save_mappings()
    return {"short_url": f"/s/{short_id}"}

@app.get("/s/{short_id}")
def redirect_url(short_id: str):
    if short_id in url_mapping:
        return {"url": url_mapping[short_id]}
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/urls")
def get_all_urls():
    return url_mapping

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
