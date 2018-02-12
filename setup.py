try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from setuptools import find_packages

setup(
    name='lqmt',
    version='1.4.1',
    description='Flexible framework that allows automation to process cyber threat information and update endpoint defense tools',
    long_description='The Last Quarter Mile Toolset is flexible framework that allows automation to process cyber threat information (CTI) and update endpoint defense tools.',
    url='https://github.com/anl-cyberscience/LQMToolset/',
    author='The CFM Team',
    author_email='fedhelp@anl.gov',
    classifiers=[
        # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers

        # How mature is this project? Common values are
        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Security',

        # Pick your license as you wish (should match 'license' above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='firewall endpoint last quarter mile toolset palo alto syslog checkpoint flextext',
    packages=find_packages(exclude=['contrib', 'doc', 'tests*']),
    install_requires=[
        'lxml',
        'netaddr',
        'pan-python',
        'toml',
        'FlexTransform>=1.2.1',
        'requests',
        'arrow'
    ],
    entry_points={
        'console_scripts': [
            'lqmt = lqmt.LQMT:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose']
)
