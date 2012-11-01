from setuptools import setup
from setuptools import find_packages
#import sys
import os

version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()


setup(name='loadwarrior',
      version=version,
      description="Graphite + locust for load generation and metrics",
      long_description=README + CHANGES,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='whit',
      author_email='whit at surveymonkey dot com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "salt",
        "cliff",
        "requests"
      ],
      entry_points="""
      [console_scripts]
      lw=loadwarrior.cli.main
      [loadwarrior.cli]
      start=loadwarrior.cli.start
      stop=loadwarrior.cli.stop
      incr=loadwarrior.cli.incr
      dec=loadwarrior.cli.dec
      """,
      )
