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

# Get template files from 'views' only.
bottle.TEMPLATE_PATH = ['./views/']

def run():
    config.cfg = config.Config('config.xml')
    config.cfg.load_fromxml()

    users.init(config.cfg.authentication)

    # Start the web service
    debug = False
    if config.cfg.server_mode == 'development': debug = True

    bottle.run(reloader = False,
               debug = debug,
               host = config.cfg.server_host,
               port = config.cfg.server_port)

