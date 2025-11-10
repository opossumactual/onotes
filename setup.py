#!/usr/bin/env python3
"""
Setup script for oNotes - A TUI Notes Application
"""

from setuptools import setup

setup(
    name="onotes",
    version="1.0.0",
    description="A terminal-based notes application inspired by macOS Notes",
    author="Your Name",
    py_modules=["notes"],
    install_requires=[
        "textual==0.47.1",
    ],
    entry_points={
        "console_scripts": [
            "onotes=notes:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
