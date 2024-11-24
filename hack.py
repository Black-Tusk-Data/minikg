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

    # knowledge_domain="Physics history",
    # entity_types=[
    #     "PERSON",
    #     "PLACE",
    #     "EVENT",
    #     "ORGANIZATION",
    #     "SCIENTIFIC DISCOVERY",
    # ],
    # input_dir=Path("./tmp"),

    knowledge_domain="Software engineering",
    entity_types=[
        "MODULE",
        "CLASS",
        "FUNCTION",
        "CODE_EXAMPLE",
        "CONCEPT",
    ],
    input_dir=Path("./input"),
    # document_desc="",

    persist_dir=Path("./cache"),
    input_file_exp="**/*.txt",
    max_chunk_lines=50,
    chunk_overlap_lines=5,
    version=1,
)


def main():
    # from IPython import embed; embed()
    api = Api(config=config)
    # api.build_kg()
    # api.visualize_kg()

    r = api.search_kg(
        "How can I most easily implement a persistent key-value store in Python?",
        k=3
    )
    print("R:", r)
    return


if __name__ == '__main__':
    main()
