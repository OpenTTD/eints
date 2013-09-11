"""
Projects overview page.
"""
from webtranslate.bottle import route, template
from webtranslate.protect import protected
from webtranslate import config

@route('/userprofile', method = 'GET')
@protected(['userprofile', '-', '-'])
def userprofile(userauth):
    """
    Get an overview of the (write) access rights of a user in every project.
    """
    all_languages = set()
    for pmd in config.cache.projects.values():
        all_languages.update(pmd.overview)

    prjdata = []
    languages = set()
    is_owner = False
    for pmd in config.cache.projects.values():
        if userauth.may_read("projsettings", pmd.name, "-"):
            is_owner = True
            prjdata.append((pmd, True, {}))
        else:
            langs = {}
            for lngname in all_languages:
                lstate = pmd.overview.get(lngname)
                if lstate is not None:
                    if userauth.may_read("string", pmd.name, lngname):
                        langs[lngname] = (True, lstate)
                else:
                    if userauth.may_read("makelanguage", pmd.name, lngname):
                        langs[lngname] = (False, ["", "", "", "", pmd.blang_count])

            languages.update(langs)
            if len(langs) > 0:
                prjdata.append((pmd, False, langs))

    prjdata.sort(key = lambda p: p[0].human_name.lower())
    return template('userprofile', userauth = userauth, prjdata = prjdata, is_owner = is_owner, languages = sorted(languages))

