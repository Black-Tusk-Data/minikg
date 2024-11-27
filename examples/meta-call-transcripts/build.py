#!/usr/bin/env python3

from conf import config

from minikg.api import Api


def main():
    api = Api(config=config)
    api.build_kg()
    return


if __name__ == '__main__':
    main()
