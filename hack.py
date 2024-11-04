#!/usr/bin/env python3

import logging
import os
from pathlib import Path

from minikg.api import Api
from minikg.models import MiniKgConfig


LOG_FMT = (
    f"%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s"
)

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")),
    format=LOG_FMT,
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

config = MiniKgConfig(
    knowledge_domain="Physics history",
    input_dir=Path("./input"),
    persist_dir=Path("./cache"),
    input_file_exp="**/*.txt",
    max_chunk_lines=200,
    chunk_overlap_lines=20,
)


def main():
    api = Api(config=config)
    api.build_kg()
    return
