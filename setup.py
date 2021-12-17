#!/usr/bin/env python3

from setuptools import setup

setup(
        name="librfap",
        version="pre-alpha",
        description="Python client library for rfap",
        url="https://github.com/alexcoder04/librfap",
        license="GNU GPLv3",
        packages=["librfap"],
        install_requires=[
            "setuptools",
            "pyyaml"
            ]
        )

