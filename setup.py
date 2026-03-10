"""
Setup script for Audience Intelligence — Multi-Platform Comment Exporters
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="audience-intelligence",
    version="1.1.0",
    author="Quantum Merlin Ltd",
    author_email="hello@quantummerlin.com",
    description="Multi-platform comment scrapers and report generator for audience intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://audienceintelligence.quantummerlin.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fb-export=fb_comment_exporter.cli:main",
            "ig-export=ig_comment_exporter.cli:main",
            "yt-export=yt_comment_exporter.cli:main",
            "report-gen=report_generator.cli:main",
        ],
    },
    keywords="facebook instagram youtube comments scraper exporter social-media analytics audience-intelligence",
)