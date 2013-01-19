"""
Main program.
"""
from webtranslate import bottle, users, projects

from webtranslate.pages import root as root_page
from webtranslate.pages import projects as projects_page
from webtranslate.pages import project as project_page
from webtranslate.pages import language as language_page

def run():
    # Initialize application
    users.users.load()
    projects.projects.load()

    # Start web service
    bottle.debug(True)
    bottle.run(host='localhost', port=8000)

