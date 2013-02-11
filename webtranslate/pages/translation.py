from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import data, config

@route('/translation/<project>/<language>', method = 'GET')
@protected(['translation', 'project', 'language'])
def project(project, language):
    pmd = config.cache.get_pmd(project)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(language)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    blng = pdata.get_base_language() # As above we established there is at least one language, this should work.
    if blng == lng:
        abort(404, "Language is not a translation")
        return

    # A translation!
    strings = [] # list of triplets (string-name, base-change, list (case, state, lng-change))
    for sname, chgs in sorted(blng.changes.items()):
        # Get newest version in the base language.
        bchg = data.get_newest_change(chgs, None)
        if bchg is None: continue # String is not in the base language (should not happen).

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
        strings.append((sname, bchg, cstrs))

    return template('translation', proj_name = project, pdata = pdata, language = language, blng = blng, strings = strings)
