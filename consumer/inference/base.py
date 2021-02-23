import abc

class PredictorBase(abc.ABC):
    @abc.abstractmethod
    def predict(self, data):
        pass
