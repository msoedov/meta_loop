from functools import wraps

from loguru import logger


def verbose_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # run_context = args[0]
        pargs = args[1:]
        logger.info(f"Running {func.__name__} with args {pargs} and kwargs {kwargs}")
        r = func(*args, **kwargs)
        logger.info(f"Result: {r}")
        return r

    return wrapper
