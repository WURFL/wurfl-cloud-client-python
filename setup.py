from setuptools import setup
import os.path

__license__ = """
 Copyright (c) 2015 ScientiaMobile Inc.
 
 The WURFL Cloud Client is intended to be used in both open-source and
 commercial environments. To allow its use in as many situations as possible,
 the WURFL Cloud Client is dual-licensed. You may choose to use the WURFL
 Cloud Client under either the GNU GENERAL PUBLIC LICENSE, Version 2.0, or
 the MIT License.
 
 Refer to the COPYING.txt file distributed with this package.

"""
__copyright__ = "2015 ScientiaMobile Incorporated, All Rights Reserved"
__version__ = "1.1.1"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


#doc = __doc__.strip()

setup (name="wurfl-cloud",
       version=__version__,
       author="ScientiaMobile",
       author_email="support@scientiamobile.com",
       license=__license__,
       packages=['wurfl_cloud', 'wurfl_cloud.cache'],
       #description=doc,
       #long_description=read('doc/README'),
       platforms="All",
       classifiers=['Development Status :: 5 - Production/Stable',
                    'Environment :: Console',
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Telecommunications Industry',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Database :: Front-Ends',
                    'Topic :: Internet :: WAP',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                    'Topic :: Utilities'
                    ])

