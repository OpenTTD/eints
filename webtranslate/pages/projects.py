"""
Projects overview page.
"""

from .. import config
from ..bottle import route
from ..protect import protected
from ..utils import template


@route("/projects", method="GET")
@protected(["projects", "-", "-"])
def root(userauth):
    # projs: C{list} of L{ProjectMetaData}
    projs = sorted(config.cache.projects.values(), key=lambda p: p.human_name.lower())
    return template("projects", userauth=userauth, projects=projs)
