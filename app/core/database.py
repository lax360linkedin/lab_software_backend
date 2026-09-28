import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

client: Optional[MongoClient] = None
db: Optional[Database] = None


def get_database() -> Database:
    global client, db
    if client is None:
        try:
            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            db = client[settings.DATABASE_NAME]
            # Ping database to verify connection immediately
            client.admin.command("ping")
            logger.info("Successfully connected to MongoDB (%s)", settings.DATABASE_NAME)
        except Exception as exc:
            logger.error("Failed to connect to MongoDB: %s", exc)
            raise exc
    return db


def init_db() -> None:
    """
    Ensure required unique indexes are created on startup:
    - users.email (unique)
    - users.userId (unique)
    - labs.labId (unique)
    """
    database = get_database()

    try:
        database.users.create_index("email", unique=True, name="uniq_user_email")
        database.users.create_index("userId", unique=True, name="uniq_user_id")
        database.labs.create_index("labId", unique=True, name="uniq_lab_id")
        logger.info("MongoDB unique indexes successfully verified/created")
    except Exception as exc:
        logger.warning("Notice on index creation: %s", exc)


def close_db() -> None:
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None
        logger.info("MongoDB connection closed")
