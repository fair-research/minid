from setuptools import setup, find_packages
import os

version = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'minid_client', 'version.py')) as f:
    exec(f.read(), {}, version)

# Get the long description from the README file
with open(os.path.join(here, 'README.rst')) as f:
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
    version=version['__VERSION__'],
    description='BD2K Minimum Viable Identifier',
    long_description=long_description,
    url='http://minid.bd2k.org/',
    author='Kyle Chard',
    author_email='chard@uchicago.edu',
    packages=find_packages(),
    install_requires=[
        'globus-sdk',
        'globus-identifiers-client'
    ],
    dependency_links=[
        'git+https://github.com/nickolausds/globus-identifiers-client'
        '@argument-field-changes#egg=globus-identifiers-client',
        'git+https://github.com/NickolausDS/globus-sdk-python'
        '@feature/native_auth#egg=globus-sdk-python'
    ],
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'minid = minid_client.commands.main:main',
        ]
    }
)
