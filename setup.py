from setuptools import setup

setup(name='minid',
    version='1.0',
    description='BD2K Minimum Viable Identifier',
    author='Kyle Chard',
    author_email='chard@uchicago.edu',
    packages=['minid-server'],
    scripts = [
        'scripts/minid.py', 'scripts/minid'
    ]
)
