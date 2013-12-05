"""
Create a new project.
"""
from webtranslate.bottle import route, template, abort, request, redirect
from webtranslate.protect import protected
from webtranslate import config, utils, project_type

@route('/newproject', method = 'GET')
@protected(['newproject', '-', '-'])
def page_get(userauth):
    return template('newproject_form')

@route('/createproject', method = 'POST')
@protected(['createproject', '-', '-'])
def page_post(userauth):
    prjname = request.forms.name.lower().strip()
    acceptance = utils.verify_name(prjname, "Project identifier", True)
    if acceptance is not None:
        redirect('/newproject?message=' + acceptance)
        return

    if prjname in config.cache.projects:
        redirect('/newproject?message=' + "Project \"{}\" already exists".format(prjname))

    return template('createproject_form', prjname = prjname)

@route('/makeproject/<prjname>', method = 'POST')
@protected(['makeproject', 'prjname', '-'])
def create_project(userauth, prjname):
    acceptance = utils.verify_name(prjname, "Project identifier", True)
    if acceptance is not None:
        redirect('/newproject?message=' + acceptance)
        return

    if prjname in config.cache.projects:
        redirect('/newproject?message=' + "Project \"{}\" already exists".format(prjname))

    human_name = request.forms.humanname.strip()
    acceptance = utils.verify_name(human_name, "Full project name", False)
    if acceptance is not None:
        redirect('/newproject?message=' + acceptance)
        return

    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)
        return

    projtype = project_type.project_types["newgrf"]
    error = config.cache.create_project(prjname, human_name, projtype, url)
    if error is not None:
        abort(404, error)
        return

    message = "Successfully created project '" + prjname +"' " + utils.get_datetime_now_formatted()
    redirect('/project/{}?message={}'.format(prjname.lower(), message))
