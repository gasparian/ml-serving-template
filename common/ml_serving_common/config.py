import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout
)

class Config(object):
    __allowed = {
        "redis_ttl": int,
        "prefetch_count": int,
        "redis_host": str,
        "redis_port": int,
        "rabbit_host": str, 
        "rabbit_port": int,
        "queue_name": str,
        "exchange_type": str,
        "exchange_name": str,
        "rabbit_ttl": str
    }

    def __init__(self, **kwargs):
        self.logger = logging.getLogger()
        for arg, dtype in self.__allowed.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))
