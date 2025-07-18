import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - optimized for container
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Cap at 4 for containers
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# Memory optimization
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Logging - optimized for containers
accesslog = "-"  # Log to stdout for container logs
errorlog = "-"   # Log to stderr for container logs
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "bookdine_gunicorn"

# Server mechanics
daemon = False
pidfile = None  # Don't use pidfile in containers
user = "app"
group = "app"
tmp_upload_dir = "/tmp"

# SSL
keyfile = None
certfile = None

# Environment
raw_env = [
    f"DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE', 'BookDine.settings.production')}",
]

# Hooks for better container integration
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
