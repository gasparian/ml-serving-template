import os
from ml_serving_common import Config as ServingConfig

class ClusteringConfig(ServingConfig):
    __allowed = {
        "min_cluster_size": int,
        "center_fasttext_vectors": int
    }

    def __init__(self, **kwargs):
        super().__init__()
        for arg, dtype in self.__allowed.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))
