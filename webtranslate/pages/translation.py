from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected

@route('/translation/<project>/<language>', method = 'GET')
@protected(['translation', 'project', 'language'])
def project(project, language):
    return template('translation', project = project, language = language)
