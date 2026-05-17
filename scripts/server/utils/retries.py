import time
import random
import functools
from ..logger import logger

def retry_with_backoff(retries: int = 3, backoff_in_seconds: int = 1):
    """
    Decorator for retrying a function with exponential backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries: {e}")
                        raise
                    
                    sleep = (backoff_in_seconds * 2 ** x +
                             random.uniform(0, 1))
                    logger.warning(f"Retrying {func.__name__} in {sleep:.2f} seconds due to error: {e}")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator
