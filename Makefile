tag = $(shell git describe --abbrev=0)
ver = $(shell git describe --abbrev=0 | egrep -o '([0-9]+\.){1,10}[0-9]+' | sed -e 's/\./_/g')
name   	   = $(shell basename $(shell pwd))

.PHONY: dist distclean test

dist: 	test
	git archive --format tar --prefix $(name)-$(ver)/ -o $(name)-$(ver).tar $(tag)
	gzip -f $(name)-$(ver).tar

distclean:
	@rm -f *tar.gz
	@rm -rf doc/api
	@rm -rf doc/html

doc:	doc/api/index.html doc/html/index.html

test:	
	@python manage.py test

doc/api/index.html:
	@mkdir -p doc/api
	epydoc -c epydoc.conf --exclude migrations -o doc/api hwdoc

doc/html/index.html: doc/install.rst
	@test -n "sphinx-build" || \
		{ echo 'sphinx-build' not found during configure; exit 1; }
	@mkdir -p doc/html
	sphinx-build -q -W -b html \
		-D version="0.3" \
		-D release="0.3" \
		-d . doc doc/html 
