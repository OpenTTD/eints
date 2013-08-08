# Makefile for building the manual

RST_FILES=setup.rst strings.rst usage.rst
DEST_FILES=$(RST_FILES:.rst=.html)

.PHONY: manual clean

.SUFFIXES:
.SUFFIXES: .html .rst

manual:
	$(MAKE) -C manual html

