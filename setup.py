import json
import os
from setuptools import setup

with open('package.json') as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")

setup(
    name=package_name,
    version=package["version"],
    author=package['author'],
    packages=[package_name],
    include_package_data=True,
    license=package['license'],
    description=package.get('description', package_name),
    install_requires=[
        'dash~=1.11.0',
        'pyyaml~=5.3.1',  #building with dash-generate-components
    ],
    classifiers=[
        'Framework :: Dash',
    ],
)
