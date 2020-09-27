"""
Root page.
"""
from ..bottle import route
from ..protect import protected
from ..utils import template


@route("/", method="GET")
@protected(["root", "-", "-"])
def root(userauth):
    return template("root", userauth=userauth)
