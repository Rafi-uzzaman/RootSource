import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
threads = int(os.getenv("WEB_THREADS", "2"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "30"))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
