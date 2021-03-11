#!/usr/bin/env python3

import os
from ml_serving.server import ServingRpcCache
from ml_serving.server import Config

config = Config()
proc = ServingRpcCache(config)
proc.consume()