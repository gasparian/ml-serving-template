import os
from ml_serving import Config as ServingConfig

class ClusteringConfig(ServingConfig):
    min_cluster_size: int
    cosine_thrsh: float

    def __init__(self, **kwargs):
        super().__init__()
        for arg, dtype in self.__class__.__annotations__.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))