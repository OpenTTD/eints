"""
Projects overview page.
"""
from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config

@route('/projects', method = 'GET')
@protected(['projects', '-', '-'])
def root(userauth):
    # projs: C{list} of L{ProjectMetaData}
    projs = sorted(config.cache.projects.values(), key=lambda p: p.human_name.lower())
    return template('projects', projects = projs)

