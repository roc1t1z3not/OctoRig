from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared singleton imported by main.py (for app.state) and by route modules
# that need @limiter.limit() decorators.
limiter = Limiter(key_func=get_remote_address)
