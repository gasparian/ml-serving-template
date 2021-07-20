#!/usr/bin/env python3
from ml_serving.server import ServingQueue, ServingCache
from config import FasttextConfig
from predictor import Predictor

config = FasttextConfig()
predictor = Predictor(config.model_path)

if config.queue_only:
    proc = ServingQueue(config, predictor)
else:
    proc = ServingCache(config, predictor)
proc.consume()
