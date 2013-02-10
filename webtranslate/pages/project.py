"""
Page of a single project.
"""
from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import config

@route('/project/<proj_name>', method = 'GET')
@protected(['project', 'proj_name', '-'])
def project(proj_name):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    if pdata.base_language is None:
        base_lng = None
    else:
        base_lng = pdata.languages[pdata.base_language]

    return template('project', pdata = pdata, base_lng = base_lng)

