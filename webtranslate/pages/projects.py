"""
Projects overview page.
"""
from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import projects

@route('/projects', method = 'GET')
@protected(['projects', '-', '-'])
def root():
    projs = sorted(projects.projects.projects.values(), key = lambda p: p.dir_name.lower())
    return template('projects', projdatas = projs)

