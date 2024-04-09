# MIT License (c) 2024. Carlos Garcia, www.carlosgarciadev.com

from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "packages": ["pandas", "ofxparse"],
}

setup(
    app=APP,
    name="Transactify",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
