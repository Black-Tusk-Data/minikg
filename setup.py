#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="minikg",
    version="v0.4.0",
    description="Hackable knowledge graph builder / retriever",
    author="Liam Tengelis",
    author_email="liam.tengelis@blacktuskdata.com",
    packages=find_packages(),
    package_data={
        "": ["*.yaml"],
        "minikg": [
            "py.typed",
        ],
    },
)
