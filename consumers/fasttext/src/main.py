import os

from ml_serving_common import Config
from ml_serving_common.message_processing import run_serving_message_processor
# TO DO: replace with real class after tests
from predictor import PredictorMock as Predictor
# from predictor import Predictor

model_path = os.environ["MODEL_PATH"]
config = Config()
predictor = Predictor(model_path)
run_serving_message_processor(config, predictor)