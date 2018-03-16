from setuptools import setup, find_packages
from os import path

import minid_client

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)


setup(
    name='minid',
    version=minid_client.__VERSION__,
    description='BD2K Minimum Viable Identifier',
    long_description=long_description,
    url='http://minid.bd2k.org/',
    author='Kyle Chard',
    author_email='chard@uchicago.edu',
    packages=find_packages(),
    install_requires=install_requires,
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'minid = minid_client.minid:main'
        ]
    }
)
