import os
from dotenv import load_dotenv, find_dotenv

# Only load .env file if it exists (for local development)
# Railway and other cloud platforms provide environment variables directly
try:
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)
except Exception:
    # If dotenv loading fails, continue with system environment variables
    pass

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

_origins = os.getenv("ALLOW_ORIGINS", "*")
ALLOW_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()] or ["*"]

# NASA API Configuration
NASA_EARTHDATA_TOKEN = os.getenv("NASA_EARTHDATA_TOKEN", "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJhZml1enphbWFuIiwiZXhwIjoxNzY0MjAxNTk5LCJpYXQiOjE3NTg5ODA3NjMsImlzcyI6Imh0dHBzOi8vdXJzLmVhcnRoZGF0YS5uYXNhLmdvdiIsImlkZW50aXR5X3Byb3ZpZGVyIjoiZWRsX29wcyIsImFjciI6ImVkbCIsImFzc3VyYW5jZV9sZXZlbCI6M30.A3UEvv9NvNuFt2GGwBtiScJunBq2wvYgBu1yZZp4xVjrZLo5Auk4sOr80txxRaOJlqPuOlGhqf0k_ng2PyEimhhD_xAzjUrjHVVTsfKGVToE_JkxaUdwJzUq-k6KQXpY3wl0JfmQ3qboB1Xvj9y1QHOZRmrA3p629RWKjhsLQZ2l-RPrQrDXL60jrvZhJbbLKvOUaMW9piegrTqr-QMFeOZV5_RHs4R0wVd9qRVmvQ1a8-2z0XAmhnPqqfg0ZZeriCOuzhOlUkYFs5R4ucysl6gE3S0F1LKh_b-cBx_VD83CZ-40gmoVAbnTgKBlqXsVt-_gYTha7aa_zxy1sIcz8w")
NASA_API_KEY = os.getenv("NASA_API_KEY", "M7JQ4IxiBtyLjJjupXOev2tAcqg1EgEBQ0nagvWW")

# NASA API Base URLs
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_MODIS_BASE_URL = "https://modis.gsfc.nasa.gov/data/"
NASA_EARTHDATA_BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
