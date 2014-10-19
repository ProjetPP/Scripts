#!/usr/bin/env python3

import os
import textwrap
import datetime

script_chmod = 0o755 # u+rwx, go+rx

makefile = """
PYTHON=python3

all: install

install:
	$(PYTHON) setup.py install

localinstall:
	$(PYTHON) setup.py install --user

run:
	gunicorn %(package_name)s:app

tests:
	$(PYTHON) run_tests.py

.PHONY: all install localinstall tests
"""

coverage_sh = """#!/bin/bash
python3-coverage run --source=%(package_name)s run_tests.py
python3-coverage html
xdg-open htmlcov/index.html
"""
run_pylint_sh = """#!/bin/bash
pylint --rcfile=.pylintrc %(package_name)s
"""

pylintrc = """[MESSAGES CONTROL]
disable=W0142
"""

run_tests_py = """#!/usr/bin/env python3
import unittest

def main(): # pragma: no cover
    testsuite = unittest.TestLoader().discover('tests/')
    results = unittest.TextTestRunner(verbosity=1).run(testsuite)
    if results.errors or results.failures:
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
"""

setup_py = """#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='%(package_name)s',
    version='0.1',
    description=%(description)r,
    url='https://github.com/ProjetPP',
    author=%(author)r,
    author_email='%(email)s',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'ppp_datamodel>=0.2',
        'ppp_core>=0.2',
    ],
    packages=[
        '%(package_name)s',
    ],
)
"""

travis_yml = """
language: python

python:
  - 3.2
  - 3.3
  - 3.4
  - pypy3

install:
    - pip install scrutinizer-ocular coverage webtest httmock requests ppp_datamodel ppp_core

before_script:
  - ./setup.py install

script:
  - coverage3 run run_tests.py

after_script:
  - ocular --data-file ".coverage"
"""

scrutinizer_yml = """checks:
    python:
        code_rating: true
        duplicate_code: true

tools:
    #    pylint:
    #        python_version: 3
    #        config_file: '.pylintrc'
    external_code_coverage: true
"""

init_py = '''"""%(description)s"""

from ppp_core import HttpRequestHandler
from .requesthandler import RequestHandler

def app(environ, start_response):
    """Function called by the WSGI server."""
    return HttpRequestHandler(environ, start_response, RequestHandler) \\
            .dispatch()
'''

requesthandler_py = '''"""Request handler of the module."""

from ppp_core.exceptions import ClientError

class RequestHandler:
    def __init__(self, request):
        # TODO: Implement this
        pass

    def answer(self):
        # TODO: Implement this
        pass
'''

license = """The MIT License (MIT)

Copyright (c) %(year)s %(author)s

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def get_nice_name():
    name = ''
    while not name.replace('_', '').isalnum():
        print('Please provide a nice name for your plugin. It should be a '
              'valid name for a folder name, so please use only '
              'alphanumerical characters and underscores.')
        name = input('name> ')
    return name

def get_package_name():
    name = ''
    while not name.replace('_', '').isalnum() and not name.islower():
        print('Please provide a package name for your plugin. It should be a '
              'valid name for a Python package, so please use only '
              'lowercase letters.')
        name = input('name> ')
    return name

def get_description():
    print('Please provide a nice description for your plugin.')
    return textwrap.fill(input('description> '))

def get_author():
    print('We need your name to put it to the license file. Just press '
          'Enter if you want to use the default attribution '
          '(“Projet Pensées Profondes”).')
    author = input('author> ') or 'Projet Pensées Profondes'
    print('We also need your email address for the setuptools data.')
    email = input('email> ')
    return (author, email)

def make_makefile(path, replacement):
    path = os.path.join(path, 'Makefile')
    with open(path, 'a') as fd:
        fd.write(makefile % replacement)

def make_coverage(path, replacement):
    path = os.path.join(path, 'coverage.sh')
    with open(path, 'a') as fd:
        fd.write(coverage_sh % replacement)
    os.chmod(path, script_chmod)

def make_pylint(path, replacement):
    path2 = os.path.join(path, 'run_pylint.sh')
    with open(path2, 'a') as fd:
        fd.write(run_pylint_sh % replacement)
    os.chmod(path2, script_chmod)
    path2 = os.path.join(path, '.pylintrc')
    with open(path2, 'a') as fd:
        fd.write(run_pylint_sh % replacement)

def make_tests(path, replacement):
    path2 = os.path.join(path, 'run_tests.py')
    with open(path2, 'a') as fd:
        fd.write(run_tests_py % replacement)
    os.chmod(path2, script_chmod)
    path2 = os.path.join(path, 'tests')
    os.mkdir(path2)

def make_license(path, replacement):
    path = os.path.join(path, 'LICENSE')
    with open(path, 'a') as fd:
        fd.write(license % replacement)

def make_travis(path, replacement):
    path = os.path.join(path, '.travis.yml')
    with open(path, 'a') as fd:
        fd.write(travis_yml % replacement)

def make_scrutinizer(path, replacement):
    path = os.path.join(path, '.scrutinizer.yml')
    with open(path, 'a') as fd:
        fd.write(scrutinizer_yml % replacement)

def make_setup(path, replacement):
    path2 = os.path.join(path, 'setup.py')
    with open(path2, 'a') as fd:
        fd.write(setup_py % replacement)

def make_package(path, replacement):
    path = os.path.join(path, replacement['package_name'])
    os.mkdir(path)
    path2 = os.path.join(path, '__init__.py')
    with open(path2, 'a') as fd:
        fd.write(init_py % replacement)
    path2 = os.path.join(path, 'requesthandler.py')
    with open(path2, 'a') as fd:
        fd.write(requesthandler_py % replacement)

def show_end_message(replacement):
    msg = ('Great! Your module has been created. Here are a few things you '
           'still have to do:\n'
           '* Setup Travis and Scrutinizer,\n'
           '* Create a git repository,\n'
           '* Set a better URL in setup.py,\n'
           '* and obviously write your plugin (start in '
           '%(package_name)s/requesthandler.py.\n'
           'Have fun!') % replacement
    print()
    print(msg)

def main():
    nice_name = get_nice_name()
    package_name = get_package_name()
    description = get_description()
    (author, email) = get_author()
    replacement = {'nice_name': nice_name,
                   'package_name': package_name,
                   'description': description,
                   'author': author,
                   'email': email,
                   'year': datetime.date.today().year
                  }
    os.mkdir(nice_name)
    for cb in (make_coverage, make_pylint, make_tests,
               make_setup, make_package,
               make_travis, make_scrutinizer,
               make_license, make_makefile,
              ):
        cb(nice_name, replacement)
    show_end_message(replacement)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
