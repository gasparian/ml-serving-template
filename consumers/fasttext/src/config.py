import os
from ml_serving_common import Config as ServingConfig

class FasttextConfig(ServingConfig):
    __allowed = {
        "model_path": str
    }

    def __init__(self, **kwargs):
        super().__init__()
        for arg, dtype in self.__allowed.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))