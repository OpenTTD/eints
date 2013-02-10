"""
Main program.
"""
from webtranslate import bottle, protect, config
from webtranslate.pages import root
from webtranslate.pages import projects
from webtranslate.pages import project
from webtranslate.pages import translation
from webtranslate.pages import upload_language
from webtranslate.pages import newproject

def run():
    config.cfg = config.Config('config.xml')
    config.cfg.load_fromxml()

    # Start the web service
    bottle.debug(True)
    bottle.run(host='localhost', port=8000)

