u"""Setup for bookhelper module.
"""

# Always prefer setuptools over distutils
from __future__ import with_statement
from __future__ import absolute_import
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, u'README.md'), encoding=u'utf-8') as f:
    long_description = f.read()

setup(
    name=u'bookhelper',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=u'0.3.0',

    description=u'Creates versions and files from a couple of mediawiki pages',
    long_description=long_description,
    include_package_data=True,
    # The project's main homepage.
    # url='https://github.com/pypa/sampleproject',

    # Author details
    author=u'Tim Heithecker',
    author_email=u'tim.heithecker@gmail.com',

    # Choose your license
    license=u'MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        u'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        u'Intended Audience :: Developers',
        u'Topic :: Open Science :: handbuch.io',

        # Pick your license as you wish (should match "license" above)
        u'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        u'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        u'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords=u'Open Science, handbuch.io ',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[]),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        u"beautifulsoup4==4.4.1",
        u"mwclient==0.8.1",
        u"pypandoc==1.1.3",
        u"requests==2.9.1",
        u"six==1.10.0",
        u"SQLAlchemy==1.0.12",
        u"celery==3.1.23",
        u"pypandoc==1.1.3",
        u"datacite>=0.2.1",
        u"PyYAML==3.11",
        u"eventlet==0.19.0",

    ],
     dependency_links=[
         u"https://github.com/inveniosoftware/datacite/archive/master.zip#egg=datacite-0.2.1",
     ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        #'dev': ['check-manifest'],
        u'test': [u'nose'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'bookhelper': [u'bookhelper/template.latex'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        u'console_scripts': [
            u'bookhelper=bookhelper.__main__:main',
        ],
    },
)
