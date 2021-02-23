import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from common import Config # type: ignore
from .message_processing import MessageProcessor # type: ignore

config = Config()
proc = MessageProcessor(config)
proc.run()
