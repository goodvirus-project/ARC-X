#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="arc-x-gaming-compressor",
    version="0.1.0",
    author="ARC-X Team",
    author_email="your.email@example.com",
    description="Ein leistungsstarkes Werkzeug zum Scannen, Komprimieren und Entpacken von Spieledateien",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ARC-X",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "arc-x-compress=src.compressor:main",
            "arc-x-extract=src.extractor:main",
        ],
    },
)