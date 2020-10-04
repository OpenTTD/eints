"""
Main program.
"""
import logging

from . import (
    bottle,
    config,
    project_type,
    users,
)
from .newgrf import language_info

# Import all pages, so they register their endpoints.
from . import static  # noqa
from .pages import (  # noqa
    delete,
    download_language,
    download_list,
    language_list,
    language_overview,
    login,
    newlanguage,
    newproject,
    project_settings,
    project,
    projects,
    root,
    string_edit,
    translation,
    upload_language,
    user_profile,
)

log = logging.getLogger(__name__)

# Get template files from 'views' only.
bottle.TEMPLATE_PATH = ["./views/"]


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
        bottle.run(reloader=False, debug=debug, host=config.cfg.server_host, port=config.cfg.server_port)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )
    log.info("Using existing config.xml")

    run()
