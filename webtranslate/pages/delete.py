from webtranslate.bottle import route, template, abort, redirect
from webtranslate.protect import protected
from webtranslate import config

@route('/delete/<prjname>/<lngname>', method = 'GET')
@protected(['delete', 'prjname', 'lngname'])
def delete_form(user, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    if pdata.base_language == lngname:
        abort(404, "Cannot delete base language!")
        return

    return template("delete_translation", pdata = pdata, lname = lngname, proj_name = prjname)

@route('/really_delete/<prjname>/<lngname>', method = 'POST')
@protected(['delete', 'prjname', 'lngname'])
def delete_submit(user, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
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
    if lngname in pdata.statistics:
        del pdata.statistics[lngname]

    config.process_project_changes(pdata) # Update changes of the project.
    config.cache.save_pmd(pmd)

    msg = "Language " + lngname + " is deleted"
    redirect('/project/{}?message={}'.format(prjname, msg))
    return
