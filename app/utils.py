import time
import functools
from logging_config import logger

def timer(func):
    """
    A decorator that logs the execution time of the decorated function.
    
    Args:
        func: The function to be timed
        
    Returns:
        wrapper: The wrapped function with timing capability
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to run")
        return result
    return wrapper