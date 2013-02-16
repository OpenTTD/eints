"""
Page of a single project.
"""
from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import config

def get_overview(pmd, lang_name):
    """
    Get the overview of the strings state of a language.

    @param pmd: Meta data of the project.
    @type  pmd: L{ProjectMetaData}

    @param lang_name: Name of the language.
    @type  lang_name: C{str}

    @return: Statistics of the strings of the language.
    @rtype:  C{list} of C{str}
    """
    counts =  pmd.overview.get(lang_name)
    if counts is not None:
        return [str(n) for n in counts]
    return ['?', '?', '?', '?', '?']


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
        transl.append((lname, get_overview(pmd, lname)))

    transl.sort()
    return template('project', proj_name = proj_name, pdata = pdata,
                    transl = transl, base_lng = base_lng,
                    bcounts = get_overview(pmd, base_lng.name))

