from setuptools import setup, find_packages

setup(name='minid',
      version='1.0',
      description='BD2K Minimum Viable Identifier',
      author='Kyle Chard',
      author_email='chard@uchicago.edu',
      packages=find_packages(),
      install_requires=['requests>=2.4.2'],
      scripts=[
          'scripts/minid.py'
      ]
)
