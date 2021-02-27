.PHONY: help clean dev docs package test

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make targets are available:"
	@echo "	 dev 	 install all deps for dev environment
	@echo "  clean   remove all old packages
	@echo "  package create pypi package zip

clean:
	rm -rf dist/*

dev:
	pip install wheel
	pip install -e .
	pip install twine
	echo "[pypi]" > ~/.pypirc
	echo "username=__token__" >> ~/.pypirc
	echo "password=${pypi-api-token}" >> ~/.pypirc
	cut -c-20 ~/.pypirc

package:
	python setup.py sdist
