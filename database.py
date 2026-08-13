import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not configured")

client = MongoClient(MONGODB_URL)

db = client["gogig_db"]

images_collection = db["images"]