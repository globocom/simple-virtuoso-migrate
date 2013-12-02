# Makefile for simple-virtuoso-migrate

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  compile    to compile .py files (just to check for syntax errors)"
	@echo "  test       to execute all simple-virtuoso-migrate tests"
	@echo "  install    to install simple-virtuoso-migrate"
	@echo "  build      to build without installing simple-virtuoso-migrate"
	@echo "  dist       to create egg for distribution"
	@echo "  publish    to publish the package to PyPI"
	@echo

clean:
	@echo "Cleaning..."
	@rm -rf build dist simple_virtuoso_migrate.egg-info *.pyc **/*.pyc *~
	@#removing test temp files
	@rm -rf `date +%Y`*

compile: clean
	@echo "Compiling source code..."
	@rm -rf simple_virtuoso_migrate/*.pyc
	@rm -rf tests/*.pyc
	@python -tt -m compileall simple_virtuoso_migrate
	@python -tt -m compileall tests

test: compile
	@make clean
	@echo "Starting tests..."
	@nosetests -s --verbose --with-coverage --cover-erase --cover-package=simple_virtuoso_migrate tests
	@make clean

install:
	@/usr/bin/env python ./setup.py install
	@pip install -r requirements_test.txt

build:
	@/usr/bin/env python ./setup.py build

dist: clean
	@python setup.py sdist

publish: dist
	@python setup.py sdist upload
