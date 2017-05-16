from setuptools import setup, find_packages

setup(
    name='minid',
    version='1.1',
    description='BD2K Minimum Viable Identifier',
    author='Kyle Chard',
    author_email='chard@uchicago.edu',
    packages=find_packages(),
    install_requires=['requests>=2.4.2'],
    entry_points={
        'console_scripts': [
            'minid = minid_client.minid:main'
        ]
    }
)
