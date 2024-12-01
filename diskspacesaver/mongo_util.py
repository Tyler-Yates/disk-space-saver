from datetime import datetime, timezone

from pymongo import MongoClient

from diskspacesaver.drive import Drive

DATABASE_NAME = "disks"
COLLECTION_NAME = "space"
TIME_SERIES_GRANULARITY = "hours"

META_FIELD = "drive_letter"
TIMESTAMP_FIELD = "timestamp"
CAPACITY_FIELD = "capacity_bytes"
FREE_FIELD = "free_bytes"


class MongoUtil:
    def __init__(self, config: dict):
        db_username = config["db_username"]
        db_password = config["db_password"]
        db_host = config["db_host"]

        uri = f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        db = client[DATABASE_NAME]

        # Get the collection or create it
        if DATABASE_NAME in client.list_database_names() and COLLECTION_NAME in db.list_collection_names():
            print(f"Collection '{COLLECTION_NAME}' already exists.")
        else:
            try:
                db.create_collection(
                    COLLECTION_NAME,
                    timeseries={
                        "timeField": TIMESTAMP_FIELD,
                        "metaField": META_FIELD,
                        "granularity": TIME_SERIES_GRANULARITY,
                    },
                )
                print(f"Time-series collection '{COLLECTION_NAME}' created successfully.")
            except Exception as e:
                print(f"Error creating collection: {e}")

        self.collection = db[COLLECTION_NAME]

        print(f"Collection {COLLECTION_NAME} has {self.collection.count_documents(filter={})} documents")

        # Save the datetime here so every document gets the same value
        self.timestamp = datetime.now(timezone.utc)

    def save_drive_info(self, drives: list[Drive]):
        documents = []
        for drive in drives:
            documents.append(
                {
                    TIMESTAMP_FIELD: self.timestamp,
                    META_FIELD: drive.drive_letter,
                    CAPACITY_FIELD: drive.capacity_bytes,
                    FREE_FIELD: drive.free_bytes,
                }
            )

        self.collection.insert_many(documents)
