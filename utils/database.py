
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")  # Changed from MONGODB_URI to MONGO_URI
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not found")

client = MongoClient(MONGO_URI)
db = client['discord_economy']  # Explicitly specify database name

def get_balance(guild_id, user_id):
    query = {"guild_id": str(guild_id), "user_id": str(user_id)}
    user_data = db.economies.find_one(query)
    
    if not user_data:
        user_data = {
            "guild_id": str(guild_id),
            "user_id": str(user_id),
            "pocket": 0,
            "bank": 0
        }
        db.economies.insert_one(user_data)
    
    return {"pocket": user_data["pocket"], "bank": user_data["bank"]}

def update_balance(guild_id, user_id, amount, location="pocket"):
    MAX_VALUE = 2**63-1
    query = {"guild_id": str(guild_id), "user_id": str(user_id)}
    
    # Get current balance
    current = db.economies.find_one(query)
    if current is None:
        current = {location: 0}
    
    # Calculate new amount with bounds check
    new_amount = min(MAX_VALUE, max(0, current.get(location, 0) + amount))
    
    # Set the new amount directly instead of using increment
    update = {"$set": {location: new_amount}}
    db.economies.update_one(query, update, upsert=True)

def save_balance(guild_id, user_id, balance):
    query = {"guild_id": str(guild_id), "user_id": str(user_id)}
    update = {"$set": balance}
    db.economies.update_one(query, update, upsert=True)
