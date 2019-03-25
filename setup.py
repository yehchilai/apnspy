# from distutils.core import setup
import os
import codecs
from setuptools import setup

from apnspy import __title__
from apnspy import __version__
from apnspy import __author__
from apnspy import __email__
from apnspy import __url__
from apnspy import __license__

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = '\n' + f.read()

setup(name=__title__,
      version=__version__,
      description='Python Distribution Utilities',
      author=__author__,
      author_email=__email__,
      long_description=long_description,
      url=__url__,
      license=__license__,
      packages=['apnspy'],
      # packages=['apnspy', 'apnspy.abc']
      install_requires=[
          'hyper','PyJWT'
      ],
      # entry_points='''
      #   [console_scripts]
      #   apnspy=apnspy.cli
      # '''
      classifiers=[
        # python trove classifiers
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
      ]
    )
    