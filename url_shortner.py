from fastapi import FastAPI, HTTPException
import string
import random
import uvicorn
from pydantic import BaseModel
import json
from fastapi.responses import RedirectResponse

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

# @app.get("/s/{short_id}")
# def redirect_url(short_id: str):
#     if short_id in url_mapping:
#         return {"url": url_mapping[short_id]}
#     raise HTTPException(status_code=404, detail="URL not found")

@app.get("/s/{short_id}")
def redirect_url(short_id: str):
    if short_id in url_mapping:
        return RedirectResponse(url=url_mapping[short_id])
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/urls")
def get_all_urls():
    return url_mapping

@app.get("/")
def test_home():
    return {"message": "URL Shortener API"}
    
@app.get("/test")
def test_shortener():
    # Test URL to shorten
    test_url = "https://www.amazon.in/hz/mobile/mission?p=iPhv1f%2BLOoJ7SxyDD3IAHS6Z7Gq2ta2zt12dskLmAvxNqyfOmj%2BKJrEfPITt3QtrJYjITHqstRHwhRBZbZvZEM4NS195PcbGjOBYW0V3w2kUbPhu5ugefipVFTXLmsjWWwxKd9KhVTzoAK2CDYObYyXUlXeaTcE%2FOYdZR3o6ChNVX5q9yK303X9rLLq0DYTgdI1s2bBaeF9Mah1X4PafIKgvIufuxzqVUoYlrprBtAZ3UEP1Q1zop48zTLtUui4BvK9YdhknzRpZltvFkV02qeJ95gNDUk%2Fe0AvxoUy%2FsUX3PZI9n8C8nx5tgs0M7o%2BCgf5vhdhhVGS2mzLNNNmKJlA741ZHkTTOskFEOQ664RSHAauYPi%2Ft661%2FyUWv8gqw4nMzI7kbvrK1j0cIX9ts1Q%3D%3D&ref_=ci_mcx_mi&pf_rd_r=DM6519DE36M3WMMDMZ0T&pf_rd_p=45c1a5b4-dab8-4658-948a-91185ec4c179&pd_rd_r=1501322e-41a5-4f98-8281-60f828c65adb&pd_rd_w=krZ9Q&pd_rd_wg=MbJHp"
    
    # Test shortening
    short_result = shorten_url(URL(url=test_url))
    short_id = short_result["short_url"].split("/")[-1]
    
    # Test redirection
    redirect_result = redirect_url(short_id)
    
    return {
        "status": "success",
        "original_url": test_url,
        "shortened_url": short_result["short_url"],
        "resolved_url": redirect_result["url"],
        "working": test_url == redirect_result["url"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
