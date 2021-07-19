#!/usr/bin/env python3
from ml_serving.server import ServingRpcPredictor, ServingPredictor
from config import FasttextConfig
from predictor import Predictor
config = FasttextConfig()
predictor = Predictor(config.model_path)

proc = ServingRpcPredictor(config, predictor)
# proc = ServingPredictor(config, predictor)
proc.consume()
