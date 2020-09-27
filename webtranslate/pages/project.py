"""
Page of a single project.
"""
from .. import config
from ..bottle import (
    abort,
    route,
)
from ..protect import protected
from ..utils import template


@route("/project/<prjname>", method="GET")
@protected(["project", "prjname", "-"])
def project(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    base_lng = pdata.get_base_language()
    transl = []
    bcounts = None
    if base_lng is not None:
        for lname, lng in pdata.languages.items():
            if lng is base_lng:
                continue
            transl.append((lng, pmd.overview.get(lname)))

        transl.sort(key=lambda x: x[0].name)

        bcounts = pmd.overview.get(base_lng.name)

    return template("project", userauth=userauth, pmd=pmd, transl=transl, base_lng=base_lng, bcounts=bcounts)
