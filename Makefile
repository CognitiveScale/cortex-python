DISTRIBUTION_NAME = $(shell python setup.py --name)
DISTRIBUTION_VERSION = $(shell python setup.py --version)

.PHONY: clean dev.install build build.alpha build.release dev.test test stage docs dev.push

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./cortex_python.egg-info

dev.install:
	pip install -r requirements-dev.txt
	pip install -r docs/requirements-docs.txt
	pip install -e .

ifdef ALPHA_BUILD
build: build.alpha
else
build: build.release
endif

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
	cd docs && make build && cd -
	# The resulting reference docs file is in docs/_build/html/index.html

docs.dev:
	sphinx-build -b html -v docs docs/_build/

docs.multi:
	sphinx-multiversion -v docs docs/_build/
	cp docs/index.html docs/_build/

docs.package:
	tar -cvzf ${DISTRIBUTION_NAME}.docs.tgz -C docs/_build .

dev.push: build.alpha
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
