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

@route('/newproject', method = 'POST')
@protected(['newproject', '-', '-'])
def page_post(user):
    human_name = request.forms.name
    acceptance = utils.verify_name(human_name)
    if acceptance is not None:
        abort(404, acceptance)
        return

    url = request.forms.url
    acceptance = utils.verify_url(url)
    if acceptance is not None:
        abort(404, acceptance)
        return


    error = config.cache.create_project(name, human_name, url)
    if error is not None:
        abort(404, error)
        return

    message = "Successfully created project '" + name +"' " + utils.get_datetime_now_formatted()
    redirect("/project/" + name.lower() + '?message=' + message)
