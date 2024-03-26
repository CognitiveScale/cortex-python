DISTRIBUTION_NAME = $(shell python setup.py --name)
DISTRIBUTION_VERSION = $(shell python setup.py --version)

.PHONY: clean dev.install build build.alpha build.release dev.test test stage dev.push docs.dev docs.multi docs.package

clean:
	rm -rf ./build
	rm -rf ./docs/_build
	rm -rf ./dist
	rm -rf ./cortex_python.egg-info
	rm -rf ./cortex-python.docs.tgz

dev.install:
	pip install poetry
	poetry install

ifdef ALPHA_BUILD
build: build.alpha
else
build: build.release
endif
docker:
	docker build -t c12e/cortex-python .

build.alpha: clean
	python setup.py egg_info --tag-build a$(shell \
		curl https://pypi.org/pypi/${DISTRIBUTION_NAME}/json | \
		jq '[ \
				.releases | \
				to_entries[] | \
				.key | \
				select(. | contains("${DISTRIBUTION_VERSION}a")) | \
				ltrimstr("${DISTRIBUTION_VERSION}a") \
			] | \
			last // "0" | \
			tonumber + 1' \
	) sdist bdist_wheel

build.release: clean
	python setup.py sdist bdist_wheel

dev.test:
	poetry run pylint --recursive=y cortex
	poetry run pytest --cache-clear  --html=coverage/test-report.html --self-contained-html --cov=cortex/ --cov-report=html:coverage --cov-report=xml:coverage.xml --cov-report=term test/unit

test:
	poetry run tox -r # tox runs make dev.test internally

stage:
	git fetch --all
	git checkout develop
	git pull
	git checkout staging
	git merge --squash develop
	git commit -m "Squash from develop"
	git push
	git checkout develop

docs.dev:
	poetry run sphinx-build -b html -v docs docs/_build/

# To be removed we don't really support older versions ATM anyway..
docs.multi:
	MULTI_VERSION="false" sphinx-multiversion -v docs docs/_build/
	cp docs/index.html docs/_build/

docs.package:
	tar -cvzf ${DISTRIBUTION_NAME}.docs.tgz -C docs/_build .

dev.push: build.alpha
	poetry run twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
