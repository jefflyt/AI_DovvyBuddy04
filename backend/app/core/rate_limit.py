"""
Rate limiting configuration.

Moved here to avoid circular imports between main.py and route modules.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
