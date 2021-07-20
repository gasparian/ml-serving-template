#!/usr/bin/env python3
from ml_serving.server import ServingRpc, ServingCache
from config import FasttextConfig
from predictor import Predictor

config = FasttextConfig()
predictor = Predictor(config.model_path)

if config.rpc:
    proc = ServingRpc(config, predictor)
else:
    proc = ServingCache(config, predictor)
proc.consume()
