# This file is a part of FileStreamBot
from os import environ
from dotenv import load_dotenv

load_dotenv()


class Var(object):
    MULTI_CLIENT = False
    API_ID = int(environ.get("API_ID"))
    API_HASH = str(environ.get("API_HASH"))
    BOT_TOKEN = str(environ.get("BOT_TOKEN"))
    SLEEP_THRESHOLD = int(environ.get("SLEEP_THRESHOLD", "60"))  # 1 minte
    WORKERS = int(environ.get("WORKERS", "6"))  # 6 workers = 6 commands at once
    BIN_CHANNEL = int(
        environ.get("BIN_CHANNEL", None)
    )  # you NEED to use a CHANNEL when you're using MULTI_CLIENT
    PORT = int(environ.get("PORT", 8080))
    BIND_ADDRESS = str(environ.get("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    HAS_SSL = str(environ.get("HAS_SSL", "0").lower()) in ("1", "true", "t", "yes", "y")
    NO_PORT = str(environ.get("NO_PORT", "0").lower()) in ("1", "true", "t", "yes", "y")
    FQDN = str(environ.get("FQDN", BIND_ADDRESS))
    URL = "http{}://{}{}/".format(
            "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
        )

    UPDATES_CHANNEL = str(environ.get('UPDATES_CHANNEL', "Telegram"))
    ALLOWED_USERS = [x.strip("@ ") for x in str(environ.get("ALLOWED_USERS", "") or "").split(",") if x.strip("@ ")]
    KEEP_ALIVE = str(environ.get("KEEP_ALIVE", "0").lower()) in  ("1", "true", "t", "yes", "y")
    NO_UPDATE = True if environ.get("NO_UPDATE", "false") == "NO_UPDATE" else False
    CONNECTION_LIMIT = int(environ.get("CONNECTION_LIMIT", 20))
    REQUEST_LIMIT = int(environ.get("REQUEST_LIMIT", 5))
    TRUST_HEADERS: bool = str(environ.get("TRUST_HEADERS", "1").lower()) in ("1", "true", "t", "yes", "y")
    DEBUG: bool = str(environ.get("DEBUG", "0").lower()) in ("1", "true", "t", "yes", "y")
    CUSTOM_URL:str = environ.get("CUSTOM_URL", None)
    LINK_TEMPLATE:str = environ.get("LINK_TEMPLATE", "{url}/dl/{id}/{name}")
    CHUNK_SIZE: int = int(environ.get("CHUNK_SIZE", 1024 * 1024)) #bytes