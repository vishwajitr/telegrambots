from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import string
import random
import uvicorn
from pydantic import BaseModel
import pymongo
from datetime import datetime

app = FastAPI()

# Connect to MongoDB Atlas
client = pymongo.MongoClient("mongodb+srv://vishwajit:b77g7WDKOoWRPiHe@cluster0.oimfhfg.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true")
db = client["url_shortner_db"]
collection = db["url_mapping"]

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class URL(BaseModel):
    url: str

@app.post("/shorten")
def shorten_url(url_data: URL):
    short_id = generate_short_id()
    collection.insert_one({
        "short_id": short_id,
        "long_url": url_data.url,
        "created_at": datetime.now()
    })
    return {"short_url": f"/s/{short_id}"}

@app.get("/s/{short_id}")
def redirect_url(short_id: str):
    url_mapping = collection.find_one({"short_id": short_id})
    if url_mapping:
        return RedirectResponse(url=url_mapping["long_url"])
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/urls")
def get_all_urls():
    return list(collection.find({}, {"_id": 0}))

@app.get("/health")
def health_check():
    try:
        client.server_info()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/test")
def test_shortener():
    test_url = "https://www.example.com/test-path"
    short_result = shorten_url(URL(url=test_url))
    short_id = short_result["short_url"].split("/")[-1]
    url_mapping = collection.find_one({"short_id": short_id})
    
    return {
        "status": "success",
        "original_url": test_url,
        "shortened_url": short_result["short_url"],
        "resolved_url": url_mapping["long_url"] if url_mapping else None,
        "working": test_url == url_mapping["long_url"] if url_mapping else False
    }

@app.delete("/urls/{short_id}")
def delete_url(short_id: str):
    result = collection.delete_one({"short_id": short_id})
    if result.deleted_count:
        return {"status": "success", "message": f"URL with id {short_id} deleted"}
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/stats")
def get_stats():
    return {
        "total_urls": collection.count_documents({}),
        "database_size": db.command("dbstats")["dataSize"],
        "last_added": list(collection.find({}, {"_id": 0}).sort("_id", -1).limit(1))
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
