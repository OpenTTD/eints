"""
Create a new project.
"""
import re
from webtranslate.bottle import route, template, abort, request, redirect
from webtranslate.protect import protected
from webtranslate import config, data, utils

@route('/newproject', method = 'GET')
@protected(['newproject', '-', '-'])
def page_get(user):
    return template('newproject_form')

@route('/createproject', method = 'POST')
@protected(['createproject', '-', '-'])
def page_post(user):
    prjname = request.forms.name
    prjname = ''.join(prjname.lower().split())
    acceptance = utils.verify_name(prjname, "Project identifier")
    if acceptance is not None:
        abort(404, acceptance)
        return

    if prjname in config.cache.projects:
        abort(404, "Project \"{}\" already exists".format(prjname))

    return template('createproject_form', prjname = prjname)

@route('/makeproject/<prjname>', method = 'POST')
@protected(['makeproject', 'prjname', '-'])
def create_project(user, prjname):
    acceptance = utils.verify_name(prjname, "Project identifier")
    if acceptance is not None:
        abort(404, acceptance)
        return

    if prjname in config.cache.projects:
        abort(404, "Project \"{}\" already exists".format(prjname))

    human_name = request.forms.humanname
    acceptance = utils.verify_name(human_name, "Full project name")
    if acceptance is not None:
        abort(404, acceptance)
        return

    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)
        return

    error = config.cache.create_project(prjname, human_name, url)
    if error is not None:
        abort(404, error)
        return

    message = "Successfully created project '" + prjname +"' " + utils.get_datetime_now_formatted()
    redirect("/project/" + prjname.lower() + '?message=' + message)
