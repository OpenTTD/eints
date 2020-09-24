"""
Main program.
"""
import sys

from wsgiref.simple_server import WSGIRequestHandler

from webtranslate import bottle, config, users, project_type
from webtranslate.newgrf import language_info

# Import all pages, so they register their endpoints.
from webtranslate import static  # noqa
from webtranslate.pages import (  # noqa
    root,
    projects,
    project,
    newproject,
    translation,
    language_list,
    language_overview,
    upload_language,
    download_language,
    download_list,
    string_edit,
    delete,
    newlanguage,
    project_settings,
    user_profile,
    login,
)

# Get template files from 'views' only.
bottle.TEMPLATE_PATH = ["./views/"]


class NoLog200HandlerHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # Only log if the status was not successful.
        if not (200 <= int(args[1]) < 400):
            WSGIRequestHandler.log_message(self, format, *args)
            sys.stderr.flush()


def run():
    # Load basic settings from the configuration (in particular, language meta-data directories).
    config.cfg = config.Config("config.xml")
    config.cfg.load_settings_from_xml()

    # Load language meta-information.
    languages = []
    if config.cfg.stable_languages_path is not None:
        for lang in language_info.load_dir(config.cfg.stable_languages_path):
            lang.is_stable = True
            languages.append(lang)

    if config.cfg.unstable_languages_path is not None:
        # Check if any allowed project type uses unstable languages before loading them.
        unstable_used = False
        for ptype_name in config.cfg.project_types:
            ptype = project_type.project_types.get(ptype_name)
            if ptype is not None and ptype.allow_unstable_lng:
                unstable_used = True
                break

        if unstable_used:
            for lang in language_info.load_dir(config.cfg.unstable_languages_path):
                lang.is_stable = False
                languages.append(lang)

    language_info.set_all_languages(languages)

    # Load user authentication, find existing projects, and initialize authentication.
    config.cfg.load_userauth_from_xml()
    config.cache.find_projects()
    users.init(config.cfg.authentication)

    # Start the web service
    debug = False
    if config.cfg.server_mode == "development":
        debug = True

    # With 'mod_wsgi', application does not run from here.
    if config.cfg.server_mode != "mod_wsgi":
        bottle.run(
            reloader=False,
            debug=debug,
            host=config.cfg.server_host,
            port=config.cfg.server_port,
            handler_class=NoLog200HandlerHandler,
        )
