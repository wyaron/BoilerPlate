# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='boiler',
    version="0.1",
    package_dir={'boiler': 'src'},
    description="A boiler controller application for raspberry pi",
    author="Yaron Weinsberg and Meir Tsvi",
    author_email='wyaron@gmail.com',
    platforms=["raspberry"],
    license="GPLv3",
    packages=find_packages(),
    url="https://github.com/wyaron/BoilerPlate",
    include_package_data=True,
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
)
