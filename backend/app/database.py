import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "ai_guessing_game"
COLLECTION_NAME = "decision_trees"

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.collection = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        try:
            # 3-second timeout so app starts fast even if MongoDB isn't reachable
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            db = self.client[DB_NAME]
            self.collection = db[COLLECTION_NAME]
            self.is_connected = True
            print(">>> Connected to MongoDB successfully! <<<")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self.is_connected = False
            print(f">>> MongoDB not reachable ({e}). Using local tree.json fallback. <<<")

    def load_tree_data(self):
        """Fetches the latest active tree from MongoDB."""
        if self.is_connected and self.collection is not None:
            try:
                doc = self.collection.find_one({"active": True}, sort=[("_id", -1)])
                if doc and "tree" in doc:
                    return doc["tree"]
            except Exception as e:
                print(f"Error reading from MongoDB: {e}")
        return None

    def save_tree_data(self, tree_dict: dict, learned_animal: str = None):
        """Stores a new tree snapshot into MongoDB with an audit entry."""
        if self.is_connected and self.collection is not None:
            try:
                record = {
                    "active": True,
                    "tree": tree_dict,
                    "last_learned": learned_animal
                }
                # Mark older snapshots as inactive to preserve history
                self.collection.update_many({"active": True}, {"$set": {"active": False}})
                self.collection.insert_one(record)
                return True
            except Exception as e:
                print(f"Error saving to MongoDB: {e}")
        return False