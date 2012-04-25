flowspytag = $(shell git describe --abbrev=0)
flowspyver = $(shell git describe --abbrev=0 | egrep -o '([0-9]+\.){1,10}[0-9]+' | sed -e 's/\./_/g')
name   	   = $(shell basename $(shell pwd))

.PHONY: dist distclean

dist: 
	git archive --format tar --prefix $(name)-$(flowspyver)/ -o $(name)-$(flowspyver).tar $(flowspytag)
	gzip -f $(name)-$(flowspyver).tar
distclean:
	@rm -f *tar.gz

