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
    base_lng = pdata.get_base_language()
    transl = []
    for lname, lng in pdata.languages.items():
        if lng is base_lng: continue

        counts =  pmd.overview.get(lname)
        if counts is not None:
            counts = [str(n) for n in counts]
        else:
            counts = ['?', '?', '?', '?']

        transl.append((lname, counts))

    transl.sort()
    return template('project', proj_name = proj_name, pdata = pdata, transl = transl, base_lng = base_lng)

