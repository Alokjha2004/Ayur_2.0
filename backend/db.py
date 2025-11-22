from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))


db_name = os.getenv("MONGO_URI").split("/")[-1].split("?")[0] 
db = client[db_name]

collection = db["plant_uses"]

def get_use_from_db(scientific_name):
    print(f" Searching DB for: '{scientific_name}'")
    record = collection.find_one({"name": scientific_name})
    print(f" DB Record Found: {record}")
    return record.get("uses") if record else None

def store_use_to_db(scientific_name, uses):
    print(f" Storing to DB: '{scientific_name}'")
    result = collection.insert_one({"name": scientific_name, "uses": uses})
    print(f"Inserted ID: {result.inserted_id}")
