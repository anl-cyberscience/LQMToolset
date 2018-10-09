try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from setuptools import find_packages

setup(
    name='lqmt',
    version='1.4.3',
    description='Flexible framework that allows automation to process cyber threat information and update endpoint defense tools',
    long_description='The Last Quarter Mile Toolset is flexible framework that allows automation to process cyber threat information (CTI) and update endpoint defense tools.',
    url='https://github.com/anl-cyberscience/LQMToolset/',
    author='The CFM Team',
    author_email='fedhelp@anl.gov',
    classifiers=[
        # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable'

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Security',

        # Pick your license as you wish (should match 'license' above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5+',
    ],
    keywords='firewall endpoint last quarter mile toolset palo alto syslog checkpoint flextext',
    packages=find_packages(exclude=['docs', 'test']),
    install_requires=[
        'lxml',
        'netaddr',
        'pan-python',
        'toml',
        'FlexTransform>=1.2.1',
        'requests',
        'arrow',
        'stix',
        'stix-ramrod',
        'jsonpath-rw',
        'pyshark',
        'pyparsing',
        'idstools',
        'xmltodict'
    ],
    entry_points={
        'console_scripts': [
            'lqmt = lqmt.LQMT:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose']
)
