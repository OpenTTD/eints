"""
Download a language file.
"""

from .. import (
    config,
    data,
)
from ..bottle import (
    abort,
    response,
    route,
)
from ..protect import protected


def plain_langfile(lines, text_type, text):
    """
    Add the L{text} to the L{lines} to give a normal language file.

    @param lines: Lines of output already created. Updated-in-place.
    @type  lines: C{list} of C{str}

    @param text_type: Type of text being added.
    @type  text_type: C{str}

    @param text: Actual text (of type L{text_type}) to add.
    @type  text: C{str}
    """
    if text_type == "credits":
        return
    lines.append(text)


def annotated_langfile(lines, text_type, text):
    """
    Add the L{text} to the L{lines} to give an annotated language file.

    @param lines: Lines of output already created. Updated-in-place.
    @type  lines: C{list} of C{str}

    @param text_type: Type of text being added.
    @type  text_type: C{str}

    @param text: Actual text (of type L{text_type}) to add.
    @type  text: C{str}
    """
    lines.append(text_type + ":" + text)


def make_langfile(pdata, base_lng, lng, add_func):
    """
    Construct a language file.

    @param pdata: Project data.
    @type  pdata: L{Project}

    @param base_lng: Base language.
    @type  base_lng: L{Language}

    @param lng: Language to output.
    @type  lng: L{Language}

    @param add_func: Function to add text to the output.
    @type  add_func: C{function}

    @return: Text containing the language file.
    @rtype:  C{str}
    """
    projtype = pdata.projtype
    if projtype.allow_case:
        lng_case = lng.case
    else:
        lng_case = [""]  # Suppress writing of non-default cases if the project doesn't allow them.

    sdict = pdata.statistics
    sdict = sdict.get(lng.name)  # Statistics dict for the queried language.
    if sdict is None:
        abort(404, "Missing language statistics")
        return None

    lines = []
    for skel_type, skel_value in pdata.skeleton:
        if skel_type == "literal":
            add_func(lines, skel_type, skel_value)
            continue
        if skel_type == "string":
            column, sname = skel_value
            chgs = lng.changes.get(sname)
            if chgs is not None:
                cstates = sdict[sname]
                # Language has sorted cases, thus the default case comes first.
                for case in lng_case:
                    chg = data.get_newest_change(chgs, case)
                    if chg is not None:
                        if case == "":
                            line = sname
                        else:
                            line = sname + "." + case

                        if lng == base_lng:
                            text = chg.base_text.text
                        else:
                            text = chg.new_text.text
                            if case != "" and text == "":
                                # Suppress printing of empty non-default cases in translations.
                                continue
                            cstate = next(se for c, se in cstates if c == case)
                            if cstate == data.INVALID:
                                # Suppress invalid translations.
                                continue

                        length = column - len(line)
                        if length < 0:
                            length = 0
                        add_func(lines, skel_type, line + (" " * length) + ":" + text)
                        if chg.user is not None:
                            add_func(lines, "credits", chg.user)
            continue

        if projtype.has_grflangid and skel_type == "grflangid":
            add_func(lines, skel_type, "##grflangid 0x{:02x}".format(lng.grflangid))
            continue

        if skel_type == "plural":
            if lng.plural is not None:
                add_func(lines, skel_type, "##plural {:d}".format(lng.plural))
            continue

        if skel_type == "case":
            cases = [c for c in lng.case if c != ""]
            if projtype.allow_case and len(cases) > 0:
                add_func(lines, skel_type, "##case " + " ".join(cases))
            continue

        if skel_type == "gender":
            if projtype.allow_gender and len(lng.gender) > 0:
                add_func(lines, skel_type, "##gender " + " ".join(lng.gender))
            continue

        if skel_type == "pragma":
            content = lng.custom_pragmas.get(skel_value)
            if content is not None:
                add_func(lines, skel_type, content)
            continue

    return "\n".join(lines) + "\n"


@route("/download/<prjname>/<lngname>", method="GET")
@protected(["download", "prjname", "lngname"])
def download(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata
    base_lng = pdata.get_base_language()

    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return None

    response.content_type = "text/plain; charset=UTF-8"
    return make_langfile(pdata, base_lng, lng, plain_langfile)


@route("/annotate/<prjname>/<lngname>", method="GET")
@protected(["annotate", "prjname", "lngname"])
def annotate(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata
    base_lng = pdata.get_base_language()

    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return None

    response.content_type = "text/plain; charset=UTF-8"
    return make_langfile(pdata, base_lng, lng, annotated_langfile)
