# retry.py
import time
import logging
import functools

logger = logging.getLogger(__name__)

# Number of times to retry before giving up
MAX_RETRIES = 3

# Starting wait time in seconds - doubles after each failure
BASE_WAIT = 2

# ------------------------------------------------------------------ #
# Decorator                                                           #
# ------------------------------------------------------------------ #

def retry(func):
    # This is the decorator that wraps any function with retry logic
    # You apply it by writing @retry above a function definition

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # *args and **kwargs mean the wrapper accepts whatever arguments
        # the original function accepts - it passes them through unchanged

        attempt = 0

        while attempt < MAX_RETRIES:
            try:
                # Try to run the original function
                return func(*args, **kwargs)

            except Exception as e:
                attempt += 1
                wait_time = BASE_WAIT ** attempt  # 2, 4, 8 seconds

                if attempt < MAX_RETRIES:
                    # Log the failure and wait before retrying
                    logger.warning(
                        "Attempt %d failed for %s - retrying in %ds - error: %s",
                        attempt, func.__name__, wait_time, str(e)
                    )
                    time.sleep(wait_time)

                else:
                    # All retries exhausted - log and raise the error
                    logger.error(
                        "All %d attempts failed for %s - error: %s",
                        MAX_RETRIES, func.__name__, str(e)
                    )
                    raise

    return wrapper