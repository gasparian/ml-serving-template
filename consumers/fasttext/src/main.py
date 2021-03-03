import os

from ml_serving_common.message_processing import run_serving_message_processor
from config import FasttextConfig
from predictor import PredictorMock, Predictor
config = FasttextConfig()
try:
    predictor = Predictor(config.model_path)
except:
    predictor = PredictorMock()
    config.logger.info("Using fasttext mock")

run_serving_message_processor(config, predictor)