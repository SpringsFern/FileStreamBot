from os import environ
from dotenv import load_dotenv

load_dotenv("web.env")

class Var(object):
    DATABASE_URL=environ.get("DATABASE_URL")
    SESSION_NAME=environ.get("SESSION_NAME")
    HAS_SSL = str(environ.get("HAS_SSL", "0").lower()) in ("1", "true", "t", "yes", "y")
    NO_PORT = str(environ.get("NO_PORT", "0").lower()) in ("1", "true", "t", "yes", "y")
    FQDN = str(environ.get("FQDN"))
    PORT=environ.get("PORT", None)
    URL = "http{}://{}{}/".format(
            "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
        )
    DL_URL = environ.get("DL_URL")
    TN_API=environ.get("TN_API")
    DEBUG=str(environ.get("DEBUG", "0").lower()) in ("1", "true", "t", "yes", "y")