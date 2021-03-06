#!/usr/bin/env python3

import os

from ml_serving.server import ServingRpcPredictor, ServingPredictor
from config import FasttextConfig
from predictor import PredictorMock, Predictor
config = FasttextConfig()
use_mock = int(os.environ["USE_MOCK"])
if use_mock:
    config.logger.info("Using fasttext mock")
    predictor = PredictorMock()
else:
    try:
        predictor = Predictor(config.model_path)
        config.logger.info("Using fasttext model")
    except:
        config.logger.warning("Could not find fasttext model. Using fasttext mock instead")
        predictor = PredictorMock()

proc = ServingRpcPredictor(config, predictor)
# proc = ServingPredictor(config, predictor)
proc.consume()
