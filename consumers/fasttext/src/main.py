import os
os.sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) # type: ignore

from common.message_processing import runMessageProcessor

# TO DO: replace with real class after tests
from predictor import PredictorMock as Predictor
# from predictor import Predictor

model_path = os.environ["MODEL_PATH"]
predictor = Predictor(model_path)
runMessageProcessor(predictor)