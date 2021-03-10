import os
from ml_serving import Config as ServingConfig

class FasttextConfig(ServingConfig):
    __allowed = {
        "redis_ttl": int,
        "model_path": str
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.redis_nodes = self.parse_hosts(os.environ["REDIS_NODES"])
        for arg, dtype in self.__allowed.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))