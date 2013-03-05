"""
Projects overview page.
"""
from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config

@route('/projects', method = 'GET')
@protected(['projects', '-', '-'])
def root(user):
    # projs: C{list} of L{ProjectMetaData}
    projs = sorted(config.cache.projects.values(), key=lambda p: p.name)
    return template('projects', projects = projs)

