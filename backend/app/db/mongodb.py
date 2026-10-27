from typing import Optional
import time
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

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
        # Test ping to verify credentials and IP access
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
