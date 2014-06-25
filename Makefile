# $Id: Makefile,v 1.6 2008/10/29 01:01:35 ghantoos Exp $
#

PYTHON=/usr/bin/python
DESTDIR=/
BUILDIR=$(CURDIR)/debian/django-netman
PROJECT=django-netman
VERSION=`$(PYTHON) setup.py --version | cut -d '-' -f 1`

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

bumpversion:
	git-dch --auto --git-author -N $(VERSION)
	git add debian/changelog
	git commit -m "Automatically updated changelog for version $(VERSION)"
	git tag --force v$(VERSION)

push:
	git push && git push --tags

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=..
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot

clean:
	$(PYTHON) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/ MANIFEST
	find . -name '*.pyc' -delete
