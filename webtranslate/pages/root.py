"""
Root page.
"""
from webtranslate.bottle import HTTPResponse, route
from webtranslate.utils import template
from webtranslate.protect import protected


@route("/", method="GET")
@protected(["root", "-", "-"])
def root(userauth):
    return template("root", userauth=userauth)


@route("/healthz", method="GET")
def healthz():
    return HTTPResponse("200: OK", status=200, headers={"content-type": "text/plain"})
