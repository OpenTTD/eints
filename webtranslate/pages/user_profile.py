"""
Projects overview page.
"""
from webtranslate.bottle import route
from webtranslate.utils import template
from webtranslate.protect import protected
from webtranslate import config, data
from webtranslate.newgrf import language_info

@route('/userprofile', method = 'GET')
@protected(['userprofile', '-', '-'])
def userprofile(userauth):
    """
    Get an overview of the (write) access rights of a user in every project.
    """
    prjdata = []
    languages = {}
    is_owner = False
    for pmd in config.cache.projects.values():
        owner = userauth.may_read("projsettings", pmd.name, "-")
        is_owner |= owner
        langs = {}
        for lang in language_info.all_languages:
            lngname = lang.isocode
            lstate = pmd.overview.get(lngname)
            exist = False
            translator = False
            if lstate is not None:
                exist = True
                translator = userauth.may_read("string", pmd.name, lngname)
            else:
                lstate = [ 0 for i in range(data.MAX_STATE) ]
                lstate[data.MISSING] = pmd.blang_count
                translator = userauth.may_read("makelanguage", pmd.name, lngname)

            langs[lngname] = (exist, lstate, translator)

            if translator and not owner:
                # Collect languages with translator access, but do not spam language list due to owner access
                languages[lngname] = lang

        prjdata.append((pmd, owner, langs))

    prjdata.sort(key = lambda p: p[0].human_name.lower())
    return template('userprofile', userauth = userauth, prjdata = prjdata, is_owner = is_owner, lnginfos = sorted(languages.values(), key=lambda x:x.isocode))

