"""Rate limiting middleware для API."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter instance
# Использует IP адрес клиента как ключ для rate limiting
limiter = Limiter(key_func=get_remote_address)
