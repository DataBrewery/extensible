#!/usr/bin/env python

from distutils.core import setup

# To use a consistent encoding
from typing import List, Dict
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="Distutils",
    version="1.0",
    description="Mechanisms for providing extensible application architecture",
    long_description=long_description,

    url="",

    # Author details
    author = "Stefan Urbanek",
    author_email = "stefan.urbanek@gmail.com",
    license = "MIT",

    # Packages
    packages=["extensible"],

    package_data={
        "": ["*.txt", "*.rst"],
    },

    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",

        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities"

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
