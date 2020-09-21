"""
Root page.
"""
from webtranslate.bottle import route
from webtranslate.utils import template
from webtranslate.protect import protected


@route("/", method="GET")
@protected(["root", "-", "-"])
def root(userauth):
    return template("root", userauth=userauth)
