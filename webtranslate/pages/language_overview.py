from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config
import operator

@route('/languages', methog = "GET")
@protected(['languages', '-', '-'])
def languages(user):
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
def language(user, lngname):
    """
    Get an overview of the state of the given language in every project.

    @param lngname: Name of the language (isocode).
    @type  lngname: C{str}
    """
    prjdata = []
    for pmd in config.cache.projects.values():
        lstate = pmd.overview.get(lngname)
        if lstate is not None:
            prjdata.append((pmd, lstate))

    prjdata.sort(key = lambda x: x[0].name)
    return template('language', lngname = lngname, prjdata = prjdata)
