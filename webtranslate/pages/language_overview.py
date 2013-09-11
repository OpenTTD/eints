from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config
import operator

@route('/languages', method = "GET")
@protected(['languages', '-', '-'])
def languages(userauth):
    """
    Get an overview of used languages over all projects.
    """
    languages = set()
    for pmd in config.cache.projects.values():
        languages.update(pmd.overview)

    languages = sorted(languages)
    return template('languages', lng_data = languages)

@route('/language/<lngname>', method = 'GET')
@protected(['language', '-', 'lngname'])
def language(userauth, lngname):
    """
    Get an overview of the state of the given language in every project.

    @param lngname: Name of the language (isocode).
    @type  lngname: C{str}
    """
    prjdata = []
    for pmd in config.cache.projects.values():
        lstate = pmd.overview.get(lngname)
        if lstate is not None:
            prjdata.append((pmd, True, lstate))
        else:
            prjdata.append((pmd, False, ["", "", "", "", pmd.blang_count]))

    prjdata.sort(key = lambda p: p[0].human_name.lower())
    return template('language', lngname = lngname, prjdata = prjdata)
