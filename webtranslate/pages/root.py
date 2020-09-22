"""
Root page.
"""
from ..bottle import (
    HTTPResponse,
    route,
)
from ..protect import protected
from ..utils import template


@route("/", method="GET")
@protected(["root", "-", "-"])
def root(userauth):
    return template("root", userauth=userauth)


@route("/healthz", method="GET")
def healthz():
    return HTTPResponse("200: OK", status=200, headers={"content-type": "text/plain"})
