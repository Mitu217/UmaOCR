import os

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8080))
DEBUG = os.environ.get('ENABLE_DEBUG', False)
THREADED = True
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # default is 5MB
