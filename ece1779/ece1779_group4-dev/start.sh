gunicorn -b :5001 web_frontend:frontendapp --worker-class eventlet --daemon
echo "frontend started on port 5001"

gunicorn -b :5000 memcache:webapp --worker-class eventlet --daemon
echo "memcache started on port 5000"
