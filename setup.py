from setuptools import setup

# http://stackoverflow.com/questions/9352656/python-assertionerror-when-running-nose-tests-with-coverage
from multiprocessing import util

setup(
    name = "Logolas",
    version = "1.0.0",
    author = "Ben Heiskell",
    author_email = "ben.heiskell@xdxa.org",
    description = "Logolas is a simple multi-file log scraper with an accompanying real-time web interface.",
    keywords = "logging log",
    license='MIT',
    long_description=open('README.rst').read(),
    packages=['logolas',],
    url = "http://github.com/bheiskell/logolas",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Log Analysis',
        'Topic :: System :: Logging',
    ],
    install_requires=[
        'flask==0.9',
        'sqlalchemy==0.8.0',
        'pyinotify==0.9.4',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
