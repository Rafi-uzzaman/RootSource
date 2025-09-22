bind = "0.0.0.0:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
threads = 2
keepalive = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"
