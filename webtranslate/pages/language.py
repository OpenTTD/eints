from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import data, config

@route('/language/<project>/<language>', method = 'GET')
@protected(['language', 'project', 'language'])
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
    stored = [[], [], [], [], []] # unknown, up-to-date, out-of-date, invalid, missing
    sdict = pdata.statistics
    sdict = sdict.get(language) # Statistics dict for the queried language.
    if sdict is None:
        abort(404, "Missing language statistics")
        return

    unknown = data.UNKNOWN
    for sname in blng.changes:
        state = max(s[1] for s in sdict[sname])
        if state >= unknown:
            stored[state - unknown].append(sname)

    strings = []
    for i, strs in enumerate(stored, start = unknown):
        strs.sort()
        title = data.STATE_MAP[i]
        title = title[0].upper() + title[1:]
        strings.append((title, strs))
    return template('language', proj_name = project, is_blng = (lng == blng),
                    pdata = pdata, language = language, strings = strings)
