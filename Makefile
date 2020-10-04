.PHONY: manual epydoc run venv

run: .env/pyvenv.cfg
ifeq (,$(wildcard ./config.xml))
	.env/bin/python -m webtranslate --project-root data
else
	.env/bin/python -m webtranslate.main
endif

venv: .env/pyvenv.cfg

.env/pyvenv.cfg: requirements.txt
	python3 -m venv .env
	.env/bin/pip install -r requirements.txt

manual:
	$(MAKE) -C docs

epydoc:
	epydoc -v --html "--exclude=webtranslate/bottle" -o docs/html webtranslate
	find . -name "*.pyc" -exec rm "{}" ";"
