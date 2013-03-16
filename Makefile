# Makefile for various tasks
#

.PHONY: manual epydoc run

run:
	./run

manual:
	$(MAKE) -C docs

epydoc:
	epydoc -v --html "--exclude=webtranslate/bottle" -o docs/html webtranslate
	find . -name "*.pyc" -exec rm "{}" ";"
