.PHONY: clean dev.install build dev.test test docs dev.alpha dev.push

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./cortex_client.egg-info

dev.install:
	pip install -r requirements-dev.txt
	pip install -r docs/requirements-docs.txt
	pip install -e .

build: clean
	python setup.py sdist bdist_wheel

dev.test:
	pytest --cache-clear test/unit

test:
	tox -r

stage:
	git fetch --all
	git checkout develop
	git pull
	git checkout staging
	git merge --squash develop
	git commit -m "Squash from develop"
	git push
	git checkout develop

docs:
	cd docs && make html && cd -
	# The resulting reference docs file is in docs/_build/html/index.html

TAG ?= 1
dev.alpha: clean
	python setup.py egg_info --tag-build a${TAG} sdist bdist_wheel

dev.push: dev.alpha
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
