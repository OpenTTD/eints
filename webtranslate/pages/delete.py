from webtranslate.bottle import route, template, abort, redirect
from webtranslate.protect import protected
from webtranslate import data, config

@route('/delete/<project>/<language>', method = 'GET')
@protected(['delete', 'project', 'language'])
def delete_form(project, language):
    pmd = config.cache.get_pmd(project)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(language)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    if pdata.base_language == language:
        abort(404, "Cannot delete base language!")
        return

    return template("delete_translation", pdata = pdata, lname = language, proj_name = project)

@route('/really_delete/<project>/<language>', method = 'POST')
@protected(['delete', 'project', 'language'])
def delete_submit(project, language):
    pmd = config.cache.get_pmd(project)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(language)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    if pdata.base_language == language:
        abort(404, "Cannot delete base language!")
        return

    del pdata.languages[language]
    if language in pdata.statistics:
        del pdata.statistics[language]

    config.process_project_changes(pdata) # Update changes of the project.
    config.cache.save_pmd(pmd)

    msg = "Language " + language + " is deleted"
    redirect('/project/{}?message={}'.format(project, msg))
    return
