"""
Main program.
"""
from webtranslate import bottle, protect, config, static, users
from webtranslate.pages import root
from webtranslate.pages import projects
from webtranslate.pages import project
from webtranslate.pages import newproject
from webtranslate.pages import language
from webtranslate.pages import upload_language
from webtranslate.pages import download_language
from webtranslate.pages import download_list
from webtranslate.pages import string_edit
from webtranslate.pages import delete
from webtranslate.pages import newlanguage
from webtranslate.pages import project_settings

def run():
    config.cfg = config.Config('config.xml')
    config.cfg.load_fromxml()

    users.init()

    # Start the web service
    bottle.run(reloader=False, debug=True, host='localhost', port=8000)

