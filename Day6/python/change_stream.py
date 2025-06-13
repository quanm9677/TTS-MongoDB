from pymongo import MongoClient
from bson import uuid

client = MongoClient("mongodb://localhost:27017")
db = client.library

def watch_loans():
    print("🔁 Watching new loans...")
    with db.loans.watch([{"$match": {"operationType": "insert"}}]) as stream:
        for change in stream:
            doc = change["fullDocument"]
            print(f"📘 New loan created for member {doc['member_id']}")

def watch_stock():
    print("📉 Watching stock drops...")
    with db.books.watch([
        {"$match": {"operationType": "update"}},
        {"$project": {"fullDocument.stock": 1}}
    ]) as stream:
        for change in stream:
            new_stock = change["updateDescription"]["updatedFields"].get("stock")
            if new_stock is not None and new_stock < 2:
                print(f"⚠️ Warning: Stock low ({new_stock}) for book ID {change['documentKey']['_id']}")

