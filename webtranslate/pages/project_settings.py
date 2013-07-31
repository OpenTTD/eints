"""
Settings of a project.
"""
import re
from webtranslate.bottle import route, template, abort, request, redirect, request, redirect
from webtranslate.protect import protected
from webtranslate import config, utils

@route('/projsettings/<proj_name>', method = 'GET')
@protected(['projsettings', 'proj_name', '-'])
def project_get(user, proj_name):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    return template('projsettings', proj_name = proj_name, human_name = pdata.human_name,
                    url = pdata.url)

@route('/projsettings/<proj_name>', method = 'POST')
@protected(['projsettings', 'proj_name', '-'])
def project_post(user, proj_name):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata

    # Get and check the new project name.
    human_name = request.forms.name
    acceptance = utils.verify_name(human_name, "Full project name")
    if acceptance is not None:
        abort(404, acceptance)
        return

    # Get and check the new url.
    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)

    message_parts = []
    if pdata.human_name != human_name:
        pdata.human_name = human_name
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

    redirect("/project/" + proj_name.lower() + '?message=' + message)


