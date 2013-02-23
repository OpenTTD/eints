"""
Main program.
"""
from webtranslate import bottle, protect, config, static
from webtranslate.pages import root
from webtranslate.pages import projects
from webtranslate.pages import project
from webtranslate.pages import newproject
from webtranslate.pages import language
from webtranslate.pages import upload_language
from webtranslate.pages import download_language
from webtranslate.pages import string_edit

def run():
    config.cfg = config.Config('config.xml')
    config.cfg.load_fromxml()

    # Start the web service
    bottle.debug(True)
    bottle.run(reloader=True, debug=True, host='localhost', port=8000)



