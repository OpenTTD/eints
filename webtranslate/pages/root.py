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


@route("/robots.txt", method="GET")
def robots():
    return HTTPResponse("User-agent: *\nDisallow: /", status=200, headers={"content-type": "text/plain"})
