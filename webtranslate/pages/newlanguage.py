from .. import (
    config,
    data,
    utils,
)
from ..bottle import (
    abort,
    request,
    route,
)
from ..newgrf import language_info
from ..protect import protected
from ..utils import (
    redirect,
    template,
)


@route("/newlanguage/<prjname>", method="GET")
@protected(["newlanguage", "prjname", "-"])
def new_language_get(userauth, prjname):
    """
    Form to add another language to the project.
    """
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata

    base_langs = []
    translations = []
    can_be_added = []
    for lang in pdata.get_all_languages():
        if lang.isocode == pdata.base_language:
            base_langs.append(lang)
            continue
        if lang.isocode in pdata.languages:
            translations.append(lang)
            continue
        can_be_added.append(lang)

    translations.sort(key=lambda x: x.isocode)
    can_be_added.sort(key=lambda x: x.isocode)

    return template(
        "newlanguage",
        userauth=userauth,
        pmd=pmd,
        base_langs=base_langs,
        translations=translations,
        can_be_added=can_be_added,
    )


@route("/newlanguage/<prjname>", method="POST")
@protected(["newlanguage", "prjname", "-"])
def new_language_post(userauth, prjname):
    """
    Construct the requested language.
    """
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    new_iso = request.forms.language_select

    lng_def = get_language(new_iso)
    if lng_def is None:
        msg = "No language found that can be created"
        abort(404, msg)
        return None

    return template("makelanguage", userauth=userauth, pmd=pmd, lnginfo=lng_def)


def get_language(name):
    """
    Get the language information by isocode.

    @param name: Iso code of the language.
    @type  name: C{str}

    @return: Language data, if available, else C{None}.
    @rtype:  L{LanguageData} or C{None}
    """
    for lang in language_info.all_languages:
        if lang.isocode == name:
            return lang
    return None


@route("/makelanguage/<prjname>/<lngname>", method="POST")
@protected(["makelanguage", "prjname", "lngname"])
def make_language_post(userauth, prjname, lngname):
    """
    Create the requested language.

    @param prjname: Name of the project.
    @type  prjname: C{str}

    @param lngname: Name of the language to create in the project.
    @type  lngname: C{str}
    """
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    lng_def = get_language(lngname)
    if lng_def is None:
        msg = "No language found that can be created"
        abort(404, msg)
        return

    pdata = pmd.pdata
    if lng_def.isocode in pdata.languages:
        abort(404, 'Language "{}" already exists'.format(lng_def.isocode))
        return

    projtype = pdata.projtype
    if not projtype.allow_language(lng_def):
        msg = 'Language "{}" may not be created in this project'.format(lng_def.isocode)
        abort(404, msg)
        return

    # Create the language.
    lng = data.Language(lng_def.isocode)
    lng.grflangid = lng_def.grflangid
    lng.plural = lng_def.plural

    if projtype.allow_gender:
        lng.gender = lng_def.gender
    else:
        lng.gender = []

    if projtype.allow_case:
        lng.case = lng_def.case
    else:
        lng.case = [""]

    pdata.languages[lng.name] = lng
    pdata.set_modified()
    lng.set_modified()

    config.cache.save_pmd(pmd)
    pmd.create_statistics(lng)

    msg = "Successfully created language '" + lng.name + "' " + utils.get_datetime_now_formatted()
    redirect("/translation/<prjname>/<lngname>", prjname=prjname, lngname=lng.name, message=msg)
    return
