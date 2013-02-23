"""
Create a new project.
"""
import re
from webtranslate.bottle import route, template, abort, request
from webtranslate.protect import protected
from webtranslate import config, data
from webtranslate.pages import project

@route('/newproject', method = 'GET')
@protected(['newproject', '-', '-'])
def page_get():
    return template('newproject_form')

@route('/newproject', method = 'POST')
@protected(['newproject', '-', '-'])
def page_post():
    name = request.forms.name

    if not name or not re.match('[A-Za-z][A-Za-z0-9]*$', name):
        abort(404, "Name missing or incorrect")
        return

    error = config.cache.create_project(name.lower(), name)
    if error is not None:
        abort(404, error)
        return

    #return template('project', name = name, proj_name = name.lower())
    return project.project(name.lower())
