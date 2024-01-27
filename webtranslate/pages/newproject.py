"""
Create a new project.
"""

from .. import (
    config,
    project_type,
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


@route("/newproject", method="GET")
@protected(["newproject", "-", "-"])
def page_get(userauth):
    all_ptype_names = []
    for projtype in project_type.project_types.values():
        if projtype.name in config.cfg.project_types:
            all_ptype_names.append(projtype.human_name)
    all_ptype_names.sort()
    return template("newproject_form", userauth=userauth, all_ptype_names=all_ptype_names)


@route("/createproject", method="POST")
@protected(["createproject", "-", "-"])
def page_post(userauth):
    prjname = request.forms.name.lower().strip()
    acceptance = utils.verify_name(prjname, "Project identifier", True)
    if acceptance is not None:
        redirect("/newproject", message=acceptance)
        return None

    if prjname in config.cache.projects:
        redirect("/newproject", message='Project "{}" already exists'.format(prjname))
        return None

    ptype_name = request.forms.projtype_select
    projtype = None
    for prjtp in project_type.project_types.values():
        if prjtp.human_name == ptype_name and prjtp.name in config.cfg.project_types:
            projtype = prjtp
            break
    if projtype is None:
        redirect("/newproject", message="No known project type provided")
        return None
    return template("createproject_form", userauth=userauth, projtype_name=projtype.name, prjname=prjname)


@route("/makeproject/<prjtypename>/<prjname>", method="POST")
@protected(["makeproject", "prjname", "-"])
def create_project(userauth, prjtypename, prjname):
    acceptance = utils.verify_name(prjname, "Project identifier", True)
    if acceptance is not None:
        redirect("/newproject", message=acceptance)
        return

    if prjname in config.cache.projects:
        redirect("/newproject", message='Project "{}" already exists'.format(prjname))
        return

    human_name = request.forms.humanname.strip()
    acceptance = utils.verify_name(human_name, "Full project name", False)
    if acceptance is not None:
        redirect("/newproject", message=acceptance)
        return

    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        redirect("/newproject", message=acceptance)
        return

    projtype = project_type.project_types.get(prjtypename)
    if projtype is None or projtype.name not in config.cfg.project_types:
        abort(404, "Unknown project type.")
        return

    error = config.cache.create_project(prjname, human_name, projtype, url)
    if error is not None:
        abort(404, error)
        return

    message = "Successfully created project '" + prjname + "' " + utils.get_datetime_now_formatted()
    redirect("/project/<prjname>", prjname=prjname.lower(), message=message)
