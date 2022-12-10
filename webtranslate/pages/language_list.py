"""
Download a list of language definitions.
Example::
    isocode,grflangid,filename,is_stable,name,ownname,plural,gender,case
    la_VA,0x66,latin,True,Latin,Latina,0,fp f m n mp np,acc dat abl gen

    @ivar filename: Name of language file without extension.
    @type filename: C{str}

    @ivar name: Name of the language in English.
    @type name: C{str}

    @ivar ownname: Name of the language in the language itself.
    @type ownname: C{str}

    @ivar isocode: Systematic name of the language.
    @type isocode: C{str}

    @ivar plural: Plural form number.
    @type plural: C{int}

    @ivar grflangid: Language id according to the NewGRF system.
    @type grflangid: C{int}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language.
    @type case: C{list} of C{str}

    @ivar is_stable: Whether the language is considered to be 'stable'. Default C{True}.
    @type is_stable: C{bool}


"""
from ..bottle import (
    response,
    route,
)
from ..newgrf import language_info
from ..protect import protected


@route("/language-list", method="GET")
@protected(["language-list", "-", "-"])
def language_list(userauth):
    response.content_type = "text/plain; charset=UTF-8"

    lines = ["isocode,grflangid,filename,is_stable,name,ownname,plural,gender,case"]
    langs = sorted(language_info.all_languages, key=lambda lang: lang.isocode)
    for lng in langs:
        line = "{},0x{:02x},{},{},{},{},{},{},{}".format(
            lng.isocode,
            lng.grflangid,
            lng.filename,
            lng.is_stable,
            lng.name,
            lng.ownname,
            lng.plural,
            " ".join(lng.gender),
            " ".join(lng.case),
        )
        lines.append(line)

    return "\n".join(lines) + "\n"
