try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    "description": "Test and visualization of OCT spectrometers",
    "author": "Nathan Harrington",
    "url": "https://github.com/nharringtonwasatch/Barbecue",
    "download_url": \
        "https://github.com/nharringtonwasatch/Barbecue",
    "author_email": "nharrington@wasatchphotonics.com.",
    "version": "1.0.0",
    "install_requires": ["numpy"],
    "packages": ["barbecue"],
    "scripts": [],
    "name": "Barbecue"
}

setup(**config)
