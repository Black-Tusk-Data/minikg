#!/usr/bin/env python3

import argparse
import json

from conf import config

from minikg.api import Api


argparser = argparse.ArgumentParser()
argparser.add_argument("query", type=str)
argparser.add_argument("--k", default=3, type=int)


def main():
    cli_args = argparser.parse_args()
    query = cli_args.query
    k = cli_args.k
    api = Api(config=config)
    r = api.search_kg(query, k=k)
    print(json.dumps(r, indent=2))
    return


if __name__ == '__main__':
    main()
