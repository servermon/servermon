# Release specifics
tag  = $(shell git describe --abbrev=0)
ver  = $(shell git describe --abbrev=0 | egrep -o '([0-9]+\.){1,10}[0-9]+')
ver_under  = $(shell echo $(ver) | sed -e 's/\./_/g')
name = $(shell basename $(shell pwd))

# Sphinx related stuff
VERSION         = "$(ver)"
SPHINXOPTS      = -q -W -D version=$(VERSION) -D release=$(VERSION)
SPHINXBUILD     = sphinx-build
PAPER           =
SRCDIR          = doc
BUILDDIR        = docbuild
# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
SPHINXFILES     = $(SRCDIR)/*

.PHONY: dist clean test

all:	dist

dist: 	test doc
	git archive --format tar --prefix $(name)-$(ver_under)/ -o $(name)-$(ver_under).tar $(tag)
	mkdir -p $(name)-$(ver_under)
	cp $(BUILDDIR)/text/install.txt $(name)-$(ver_under)/README
	cp $(BUILDDIR)/text/upgrade.txt $(name)-$(ver_under)/README.upgrade
	tar rf $(name)-$(ver_under).tar $(name)-$(ver_under)/README $(name)-$(ver_under)/README.upgrade
	rm -rf $(name)-$(ver_under)
	gzip -f $(name)-$(ver_under).tar

clean:
	@rm -f *tar.gz
	@rm -rf $(BUILDDIR)
	@rm -rf htmlcov

doc:	$(BUILDDIR)/api $(BUILDDIR)/html $(BUILDDIR)/text

test:
	@python servermon/manage.py test --noinput

coverage:
	@python-coverage run --source=servermon servermon/manage.py test --noinput
	@python-coverage html

$(BUILDDIR)/api:
	@mkdir -p $(BUILDDIR)
	DJANGO_SETTINGS_MODULE="servermon.settings" epydoc -c doc/epydoc.conf --exclude 'migrations|manage|settings|urls' -o $(BUILDDIR)/api servermon

$(BUILDDIR)/html: $(SPHINXFILES)
	@mkdir -p $(BUILDDIR)
	@test -n "sphinx-build" || \
		{ echo 'sphinx-build' not found during configure; exit 1; }
	sphinx-build -b html \
		-d $(BUILDDIR)/doctrees $(SRCDIR) $(BUILDDIR)/html

$(BUILDDIR)/text: $(SPHINXFILES)
	@mkdir -p $(BUILDDIR)
	@test -n "sphinx-build" || \
		{ echo 'sphinx-build' not found during configure; exit 1; }
	sphinx-build -b text \
		-d $(BUILDDIR)/doctrees $(SRCDIR) $(BUILDDIR)/text
