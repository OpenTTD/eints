"""
Page of a single project.
"""
from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import config, data


@route('/project/<prjname>', method = 'GET')
@protected(['project', 'prjname', '-'])
def project(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    base_lng = pdata.get_base_language()
    transl = []
    bcounts = None
    if base_lng is not None:
        for lname, lng in pdata.languages.items():
            if lng is base_lng: continue
            transl.append((lng, pmd.overview.get(lname)))

        transl.sort(key=lambda x: x[0].name)

        bcounts = pmd.overview.get(base_lng.name)

    return template('project', pmd = pmd,
                    transl = transl, base_lng = base_lng, bcounts = bcounts)

