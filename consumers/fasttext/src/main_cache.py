#!/usr/bin/env python3

import os
from ml_serving.server import ServingCacheQueue
from config import FasttextConfig

config = FasttextConfig()
proc = ServingCacheQueue(config)
proc.consume()