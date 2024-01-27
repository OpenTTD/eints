"""
Settings of a project.
"""

from .. import (
    config,
    utils,
)
from ..bottle import (
    abort,
    request,
    route,
)
from ..protect import protected
from ..utils import (
    redirect,
    template,
)


@route("/projsettings/<prjname>", method="GET")
@protected(["projsettings", "prjname", "-"])
def project_get(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    return template("projsettings", userauth=userauth, pmd=pmd)


@route("/projsettings/<prjname>", method="POST")
@protected(["projsettings", "prjname", "-"])
def project_post(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata

    # Get and check the new project name.
    human_name = request.forms.name.strip()
    acceptance = utils.verify_name(human_name, "Full project name", False)
    if acceptance is not None:
        redirect("/projsettings/<prjname>", prjname=prjname, message=acceptance)
        return

    # Get and check the new url.
    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)

    message_parts = []
    if pdata.human_name != human_name:
        pdata.human_name = human_name
        pmd.human_name = human_name  # Also assign the new name to the meta-data storage.
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

    redirect("/project/<prjname>", prjname=prjname.lower(), message=message)
