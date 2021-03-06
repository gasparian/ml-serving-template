import os

from ml_serving_common.message_processing import run_serving_message_processor
from config import FasttextConfig
from predictor import PredictorMock, Predictor
config = FasttextConfig()
try:
    predictor = Predictor(config.model_path)
except:
    config.logger.warning("Could not find fasttext model. Using fasttext mock instead")
    predictor = PredictorMock()

run_serving_message_processor(config, predictor)