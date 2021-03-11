#!/usr/bin/env python3

import os
from ml_serving.server import ServingRpcCache
from config import FasttextConfig

config = FasttextConfig()
proc = ServingRpcCache(config)
proc.consume()