#!/usr/bin/env python3

import logging
import os

LOG_FMT = (
    f"%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s"
)

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")),
    format=LOG_FMT,
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

from pathlib import Path

from minikg.api import Api
from minikg.models import MiniKgConfig



config = MiniKgConfig(
    knowledge_domain="technology industry",
    entity_types=[
        "ORGANIZATION",
        "EVENT",
        "PRODUCT",
        "PERSON",
        "OPPORTUNITY",
        "CHALLENGE",
    ],
    input_dir=Path("./txts"),
    document_desc="call transcript",
    persist_dir=Path("./cache"),
    input_file_exp="**/*.txt",
    max_chunk_lines=30,
    chunk_overlap_lines=5,
    version=1,
)


def main():
    # from IPython import embed; embed()
    api = Api(config=config)
    api.build_kg()
    # api.visualize_kg()

    return


if __name__ == '__main__':
    main()
