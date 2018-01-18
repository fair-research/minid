from setuptools import setup, find_packages

import minid_client

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
    url='http://minid.bd2k.org/',
    author='Kyle Chard',
    author_email='chard@uchicago.edu',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'minid = minid_client.minid:main'
        ]
    }
)
