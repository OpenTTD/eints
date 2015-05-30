"""
Main program.
"""
from webtranslate import bottle, protect, config, static, users
from webtranslate.newgrf import language_info
from webtranslate.pages import root
from webtranslate.pages import projects
from webtranslate.pages import project
from webtranslate.pages import newproject
from webtranslate.pages import translation
from webtranslate.pages import language_overview
from webtranslate.pages import upload_language
from webtranslate.pages import download_language
from webtranslate.pages import download_list
from webtranslate.pages import string_edit
from webtranslate.pages import delete
from webtranslate.pages import newlanguage
from webtranslate.pages import project_settings
from webtranslate.pages import user_profile

# Get template files from 'views' only.
bottle.TEMPLATE_PATH = ['./views/']

def run():
    # Load basic settings from the configuration (in particular, language meta-data directories).
    config.cfg = config.Config('config.xml')
    config.cfg.load_settings_from_xml()

    # Load language meta-information.
    languages = []
    if config.cfg.stable_languages_path is not None:
        languages.extend(language_info.load_dir(config.cfg.stable_languages_path))
    if config.cfg.unstable_languages_path is not None:
        languages.extend(language_info.load_dir(config.cfg.unstable_languages_path))
    language_info.set_all_languages(languages)

    # Load user authentication, find existing projects, and initialize authentication.
    config.cfg.load_userauth_from_xml()
    config.cache.find_projects()
    users.init(config.cfg.authentication)

    # Start the web service
    debug = False
    if config.cfg.server_mode == 'development': debug = True

    # With 'mod_wsgi', application does not run from here.
    if config.cfg.server_mode != 'mod_wsgi':
        bottle.run(reloader = False,
                   debug = debug,
                   host = config.cfg.server_host,
                   port = config.cfg.server_port)

