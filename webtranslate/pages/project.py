"""
Page of a single project.
"""
from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import config

@route('/project/<proj_name>', method = 'GET')
@protected(['project', 'proj_name', '-'])
def project(proj_name):
    proj = config.cache.projects.get(proj_name)
    if proj is None:
        abort(404, "Page not found")
        return

    return template('project', proj_name = proj_name) #, project = proj)

