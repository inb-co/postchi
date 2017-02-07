import sys
from distutils.core import setup

import setuptools
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='postchi',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version='0.1.0',
    description='A reliable async email sender for django',
    author='Mahdi Zareie',
    install_requires=["django==1.9.12",
                      "easy-job"],
    tests_require=['django-setuptest'],
    test_suite='setuptest.setuptest.SetupTestSuite',
    py_modules=['tests.tests'],
    author_email='mahdi.elf@gmail.com',
    url='https://github.com/inb-co/postchi',
    keywords=['postchi', 'async email sender', 'django email backend'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
