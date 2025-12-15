#!/usr/bin/env python3
"""
Setup script for Winvora.

Install Winvora and its dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Base requirements (CLI only)
base_requirements = [
    # No external dependencies for core functionality
    # Wine is an external system dependency
]

# GUI requirements for desktop platforms
gui_requirements = [
    "PyQt6>=6.0.0",
]

# Android requirements
android_requirements = [
    "kivy>=2.0.0",
    "buildozer>=1.5.0",
]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
]

setup(
    name="winvora",
    version="0.1.0",
    description="A cross-platform open-source application for running Windows software using Wine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Winvora Contributors",
    url="https://github.com/dauiau/Winvora",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=base_requirements,
    extras_require={
        "gui": gui_requirements,
        "android": android_requirements,
        "dev": dev_requirements,
        "all": gui_requirements + android_requirements,
    },
    entry_points={
        "console_scripts": [
            "winvora=cli.main:main",
            "winvora-cli=cli.main:main",
        ],
        "gui_scripts": [
            "winvora-gui=winvora:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Emulators",
    ],
    keywords="wine windows compatibility layer emulation",
)
