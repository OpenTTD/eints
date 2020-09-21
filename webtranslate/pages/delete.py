from webtranslate.bottle import route, abort
from webtranslate.utils import redirect, template
from webtranslate.protect import protected
from webtranslate import config


@route("/delete/<prjname>/<lngname>", method="GET")
@protected(["delete", "prjname", "lngname"])
def delete_form(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    if pmd.storage_type == config.STORAGE_SEPARATE_LANGUAGES:
        abort(404, "Cannot delete a language, ask the system administrator to remove the language file")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    if pdata.base_language == lngname:
        abort(404, "Cannot delete base language!")
        return

    return template("delete_translation", userauth=userauth, pmd=pmd, lng=lng)


@route("/really_delete/<prjname>/<lngname>", method="POST")
@protected(["delete", "prjname", "lngname"])
def delete_submit(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    if pmd.storage_type == config.STORAGE_SEPARATE_LANGUAGES:
        abort(404, "Cannot delete a language, ask the system administrator to remove the language file")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    if pdata.base_language == lngname:
        abort(404, "Cannot delete base language!")
        return

    del pdata.languages[lngname]
    pdata.set_modified()
    if lngname in pdata.statistics:
        del pdata.statistics[lngname]
    if lngname in pmd.overview:
        del pmd.overview[lngname]

    config.process_project_changes(pdata)  # Update changes of the project.
    config.cache.save_pmd(pmd)

    msg = "Language " + lngname + " is deleted"
    redirect("/project/<prjname>", prjname=prjname, message=msg)
    return
