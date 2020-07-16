from setuptools import setup, find_packages

setup(
    name="socketscs",
    packages=find_packages(),
    version='0.0.2',
    package_data={'socketscs': ['data/*.csv']},
    )
