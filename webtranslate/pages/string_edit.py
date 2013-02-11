from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import data, config

@route('/string/<proj_name>/<lname>/<sname>', method = 'GET')
@protected(['string', 'proj_name', 'lname'])
def project(proj_name, lname, sname):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    blng = pdata.get_base_language()
    if blng == lng:
        abort(404, "Language is not a translation")
        return

    bchgs = blng.changes.get(sname)
    if bchgs is None:
        abort(404, "String does not exist in the project")
        return

    bchg = data.get_newest_change(bchgs, None)
    if bchg is None:
        abort(404, "String has no value in the project")
        return

    # Get the newest version in the translation, for all cases.
    cases = {}
    if len(lng.case) > 0: cases = dict((c, [None]) for c in lng.case)
    cases[None] = [None]
    for chg in lng.changes.get(sname, []):
        tc = cases.get(chg.case)
        if tc[0] is None or tc[0].stamp < chg.stamp: tc[0] = chg
    cstrs = []
    for c, tc in cases.items():
        if c is None: c = ''
        cstrs.append((c, 'unknown', tc[0]))
    cstrs.sort()

    return template('string_form', proj_name = proj_name, pdata = pdata,
                    lname = lname, sname = sname, case_lst = cstrs,
                    bchg = bchg)
