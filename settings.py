import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

_origins = os.getenv("ALLOW_ORIGINS", "*")
ALLOW_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()] or ["*"]
