import os
import re
import sys
import logging
from typing import List, Dict, Union

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout
)

class Config(object):
    _allowed = {
        "prefetch_count": int,
        "queue_name": str,
        "cache_queue_name": str,
        "exchange_type": str,
        "exchange_name": str,
        "rabbit_ttl": str,
        "rabbit_heartbeat_timeout": int,
        "rabbit_blocked_connection_timeout": int
    }

    def __init__(self, **kwargs):
        self.__regex_colon = re.compile(":[0-9]")
        self.logger = logging.getLogger()
        self.rabbit_nodes = self.parse_hosts(os.environ["RABBIT_NODES"])
        for arg, dtype in self._allowed.items():
            if arg in kwargs:
                setattr(self, arg, dtype(kwargs[arg]))
            else:
                setattr(self, arg, dtype(os.environ[arg.upper()]))

    def parse_hosts(self, inp: str) -> List[Dict[str, str]]:
        splitted = inp[1:-1].strip().split()
        if not len(splitted):
            raise ValueError("Hosts parsing error: empty")
        out = []
        for s in splitted:
            colon_idx = self.__regex_colon.search(s).span()[0]
            host, port = s[:colon_idx], s[colon_idx+1:]
            out.append({
                "host": host,
                "port": port
            })
        return out