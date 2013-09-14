"""
Settings of a project.
"""
from webtranslate.bottle import route, template, abort, request, redirect, request, redirect
from webtranslate.protect import protected
from webtranslate import config, utils

@route('/projsettings/<prjname>', method = 'GET')
@protected(['projsettings', 'prjname', '-'])
def project_get(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    return template('projsettings', proj_name = prjname, human_name = pdata.human_name,
                    url = pdata.url)

@route('/projsettings/<prjname>', method = 'POST')
@protected(['projsettings', 'prjname', '-'])
def project_post(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata

    # Get and check the new project name.
    human_name = request.forms.name.strip()
    acceptance = utils.verify_name(human_name, "Full project name", False)
    if acceptance is not None:
        redirect('/projsettings/' + prjname + '?message=' + acceptance)
        return

    # Get and check the new url.
    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)

    message_parts = []
    if pdata.human_name != human_name:
        pdata.human_name = human_name
        pmd.human_name = human_name # Also assign the new name to the meta-data storage.
        message_parts.append("name")
    if pdata.url != url:
        pdata.url = url
        message_parts.append("URL")

    if len(message_parts) == 0:
        message = "Project settings are not modified"
    else:
        parts = " and ".join(message_parts)
        if len(message_parts) < 2:
            has = "has"
        else:
            has = "have"

        message = "Project {} {} been changed {}"
        message = message.format(parts, has, utils.get_datetime_now_formatted())

        config.cache.save_pmd(pmd)

    redirect("/project/" + prjname.lower() + '?message=' + message)


