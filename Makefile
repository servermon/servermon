# Sphinx related stuff
VERSION	        = "0.4.1"
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

# Release specifics
tag  = $(shell git describe --abbrev=0)
ver  = $(shell git describe --abbrev=0 | egrep -o '([0-9]+\.){1,10}[0-9]+' | sed -e 's/\./_/g')
name = $(shell basename $(shell pwd))

.PHONY: dist clean test

all:	dist

dist: 	test doc
	git archive --format tar --prefix $(name)-$(ver)/ -o $(name)-$(ver).tar $(tag)
	mkdir -p $(name)-$(ver)
	cp $(BUILDDIR)/text/install.txt $(name)-$(ver)/README
	cp $(BUILDDIR)/text/upgrade.txt $(name)-$(ver)/README.upgrade
	tar rf $(name)-$(ver).tar $(name)-$(ver)/README $(name)-$(ver)/README.upgrade
	rm -rf $(name)-$(ver)
	gzip -f $(name)-$(ver).tar

clean:
	@rm -f *tar.gz
	@rm -rf $(BUILDDIR)

doc:	$(BUILDDIR)/api $(BUILDDIR)/html $(BUILDDIR)/text

test:	
	@python manage.py test

$(BUILDDIR)/api:
	@mkdir -p $(BUILDDIR)
	epydoc -c epydoc.conf --exclude migrations -o $(BUILDDIR)/api hwdoc

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
