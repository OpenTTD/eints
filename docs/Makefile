# Makefile for building the manual

RST_FILES=setup.rst strings.rst usage.rst
DEST_FILES=$(RST_FILES:.rst=.html)

.PHONY: manual clean

.SUFFIXES:
.SUFFIXES: .html .rst

manual: $(DEST_FILES)

clean:
	for i in $(DEST_FILES);\
	do if test -f $$i;\
	   then rm $$i;\
	   fi;\
	done

%.html: %.rst
	rst2html $< $@
