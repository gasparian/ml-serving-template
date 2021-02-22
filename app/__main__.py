from .message_processing import Config, MessageProcessor # type: ignore

config = Config()
proc = MessageProcessor(config)
proc.run()
