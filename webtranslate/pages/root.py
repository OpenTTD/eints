"""
Root page.
"""
from webtranslate.bottle import route, template
from webtranslate.protect import protected

@route('/', method = 'GET')
@protected(['root', '-', '-'])
def root():
    return template('root')

