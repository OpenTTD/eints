"""
Page of a single project.
"""
from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import users, projects

@route('/projects/<name>', method = 'GET')
@protected(['project', 'name', '-'])
def project(name):
    proj = projects.projects.projects.get(name)
    if proj is None:
        abort(404, "Page not found")
        return

    return template('project', name = name, project = proj)

