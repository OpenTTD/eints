from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config, data
from webtranslate.newgrf import language_info
import operator

@route('/languages', method = "GET")
@protected(['languages', '-', '-'])
def languages(userauth):
    """
    Get an overview of used languages over all projects.
    """
    languages = sorted(language_info.all_languages, key = lambda l: l.isocode)
    return template('languages', lnginfos = languages)

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
            lstate = [ 0 for i in range(data.MAX_STATE) ]
            lstate[data.MISSING] = pmd.blang_count
            prjdata.append((pmd, False, lstate))

    prjdata.sort(key = lambda p: p[0].human_name.lower())
    return template('language', lnginfo = language_info.isocode.get(lngname), prjdata = prjdata)
