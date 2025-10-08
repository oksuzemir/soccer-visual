import time
import random
from typing import Callable, Type, Iterable

def retry(
    func: Callable,
    exceptions: Iterable[Type[BaseException]],
    tries: int = 3,
    base_delay: float = 0.8,
    max_delay: float = 4.0,
    jitter: float = 0.3
):
    """
    Basit exponential backoff retry wrapper.
    """
    attempt = 0
    while True:
        try:
            return func()
        except tuple(exceptions) as e:
            attempt += 1
            if attempt >= tries:
                raise
            sleep_time = min(base_delay * (2 ** (attempt - 1)), max_delay)
            sleep_time = sleep_time + random.uniform(0, jitter)
            time.sleep(sleep_time)