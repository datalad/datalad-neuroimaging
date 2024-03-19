# simple makefile to simplify repetitive build env management tasks under posix
# Ideas borrowed from scikit-learn's and PyMVPA Makefiles  -- thanks!

PYTHON ?= python

MODULE ?= datalad

all: clean

clean:
	$(PYTHON) setup.py clean
	rm -rf dist build bin docs/build docs/source/generated *.egg-info
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -type d -delete

bin:
	mkdir -p $@
	PYTHONPATH=bin:$(PYTHONPATH) python setup.py develop --install-dir $@


trailing-spaces:
	find $(MODULE) -name "*.py" -exec perl -pi -e 's/[ \t]*$$//' {} \;

code-analysis:
	flake8 $(MODULE) | grep -v __init__ | grep -v external
	pylint -E -i y $(MODULE)/ # -d E1103,E0611,E1101

update-changelog:
	@echo ".. This file is auto-converted from CHANGELOG.md (make update-changelog) -- do not edit\n\nChange log\n**********" > docs/source/changelog.rst
	pandoc -t rst CHANGELOG.md >> docs/source/changelog.rst

release-pypi: update-changelog
# better safe than sorry / avoid upload of stale builds
	test ! -e dist
	python setup.py sdist bdist_wheel
	twine upload dist/*

render-casts: docs/source/usecases/simple_provenance_tracking.rst.in

docs/source/usecases/reproducible_analysis.rst.in: build/casts/reproducible_analysis.json
	tools/cast2rst $^ > $@

update-buildsupport:
	git subtree pull \
		-m "Update DataLad build helper" \
		--squash \
		--prefix _datalad_buildsupport \
		https://github.com/datalad/datalad-buildsupport.git \
		master
