from typing import Optional
import logging
import time

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

from app.core.config import settings

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None
_last_check_time: float = 0.0
_is_connected: bool = False


def create_mongo_client() -> Optional[MongoClient]:
    """Create a client and check connectivity with short timeout."""
    global _mongo_client, _last_check_time, _is_connected

    uri = settings.effective_mongo_uri
    if not uri:
        return None

    now = time.time()
    # If connection previously failed, only recheck every 30 seconds
    if not _is_connected and (now - _last_check_time) < 30.0 and _mongo_client is not None:
        return None

    _last_check_time = now

    try:
        import certifi
        client = MongoClient(
            uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000,
        )
        client.admin.command("ping")
        _mongo_client = client
        _is_connected = True
        return _mongo_client
    except Exception:
        try:
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
            )
            client.admin.command("ping")
            _mongo_client = client
            _is_connected = True
            return _mongo_client
        except Exception:
            _is_connected = False
            return None


def get_database(client: Optional[MongoClient] = None) -> Optional[Database]:
    """Return the configured database, without crashing if connection fails."""
    try:
        if client is None:
            client = create_mongo_client()
        if client is None or not _is_connected:
            return None
        return client[settings.mongodb_database]
    except Exception:
        return None


def ensure_vehicle_indexes() -> None:
    """
    Create required indexes on the vehicles collection.

    Called once at application startup. Idempotent.
    """
    db = get_database()
    if db is None:
        logger.warning(
            "MongoDB not configured — skipping vehicle index creation. "
            "Set MONGODB_URI in your environment."
        )
        return

    collection = db["vehicles"]
    index_name = "uq_registration_number"
    try:
        collection.create_index(
            [("registrationNumber", ASCENDING)],
            unique=True,
            sparse=True,
            name=index_name,
        )
        logger.info("Vehicle index '%s' is ready.", index_name)
    except (DuplicateKeyError, OperationFailure, PyMongoError) as exc:
        logger.error(
            "Could not create vehicle index '%s'. "
            "Error: %s",
            index_name,
            exc,
        )
