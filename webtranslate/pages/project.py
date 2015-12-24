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

    @return: Statistics of the strings of the language, 'needs fixing' flag.
    @rtype:  C{list} of C{str}, C{bool}
    """
    counts = pmd.overview.get(lang_name)
    if counts is not None:
        needs_fixing = counts[2] != 0 or counts[3] != 0 or counts[4] != 0
        return [str(n) for n in counts], needs_fixing
    return ['?', '?', '?', '?', '?'], False


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
            counts, needs_fixing = get_overview(pmd, lname)
            transl.append((lname, counts, needs_fixing))

        transl.sort()

        bcounts = get_overview(pmd, base_lng.name)[0]

    return template('project', pmd = pmd,
                    transl = transl, base_lng = base_lng, bcounts = bcounts)

