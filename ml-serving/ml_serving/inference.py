import abc
from typing import Any

class PredictorBase(abc.ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def predict(self, data: Any) -> Any:
        pass
