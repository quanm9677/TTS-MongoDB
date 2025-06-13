from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure, PyMongoError
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from bson.binary import Binary, UuidRepresentation
from bson import Binary as BsonBinary
from datetime import datetime, timedelta, timezone
import time
import uuid

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017", retryWrites=True)
db = client.library

# Chuyển UUID Python -> BSON Binary với UuidRepresentation.STANDARD
def to_bson_uuid(uuid_obj):
    return BsonBinary.from_uuid(uuid_obj, uuid_representation=UuidRepresentation.STANDARD)

def borrow_book_with_retry(member_id, book_id, max_retries=3):
    for attempt in range(max_retries):
        session = client.start_session()

        try:
            session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", wtimeout=5000),
                read_preference=ReadPreference.PRIMARY
            )

            book = db.books.find_one({"book_id": to_bson_uuid(book_id)}, session=session)
            if not book:
                raise Exception("Book not found")
            if book["stock"] <= 0:
                raise Exception("Out of stock")

            db.books.update_one(
                {"book_id": to_bson_uuid(book_id)},
                {"$inc": {"stock": -1}},
                session=session
            )

            db.loans.insert_one(
                {
                   "loan_id": to_bson_uuid(uuid.uuid4()),
        "member_id": to_bson_uuid(member_id),
        "book_id": to_bson_uuid(book_id),
        "borrow_date": datetime.now(timezone.utc),
        "due_date": datetime.now(timezone.utc) + timedelta(days=14),
        "status": "ACTIVE"
                },
                session=session
            )

            session.commit_transaction()
            print("✅ Transaction successful")
            return

        except (ConnectionFailure, PyMongoError) as e:
            print(f"⚠️ Retrying due to error: {e} (Attempt {attempt + 1})")
            session.abort_transaction()
            time.sleep(1)
        except DuplicateKeyError as e:
            print(f"❌ Duplicate key error: {e}")
            session.abort_transaction()
            return
        except Exception as e:
            print(f"❌ Transaction failed: {e}")
            session.abort_transaction()
            return
        finally:
            session.end_session()

# Gọi hàm
borrow_book_with_retry(
    uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
    uuid.UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8")
)
