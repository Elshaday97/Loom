import time
from functools import wraps


def retry(
    max_retries: int = 4,
    initial_delay: int = 1,
    max_delay: int = 60,
    exponent: int = 2,
    exceptions=(Exception),
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            retries = 1

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if retries == max_retries:
                        raise

                    time.sleep(delay)
                    delay = min(delay * exponent, max_delay)
                    retries += 1

        return wrapper

    return decorator
