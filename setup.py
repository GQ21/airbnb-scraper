from setuptools import setup

setup(
    name="Airbnb scrapper",
    version="0.0.1",
    description="Simple Airbnb Scraper",
    author="Gintautas Jankus",
    url="https://github.com/GQ21/airbnb-scraper",
    packages=["airbnb"],
    install_requires=["pandas", "beautifulsoup4", "selenium"],
)
