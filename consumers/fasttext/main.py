import os
os.sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # type: ignore

from common.message_processing import runMessageProcessor
from predictor import PredictorMock as Predictor
# from predictor import Predictor

runMessageProcessor(Predictor)