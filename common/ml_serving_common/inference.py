import abc

class PredictorBase(abc.ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def predict(self, data):
        pass
