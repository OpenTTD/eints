"""
Upload a language file.
"""
from .. import (
    config,
    data,
    utils,
)
from ..bottle import (
    abort,
    request,
    route,
)
from ..newgrf import (
    language_file,
    language_info,
)
from ..protect import protected
from ..utils import (
    redirect,
    template,
)


@route("/upload/<prjname>", method="GET")
@protected(["upload", "prjname", "-"])
def page_get(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata
    if pdata.projtype.has_grflangid:
        return template("upload_lang", userauth=userauth, pmd=pmd)
    else:
        return template(
            "upload_lang_select",
            userauth=userauth,
            pmd=pmd,
            lnginfos=sorted(pdata.get_all_languages(), key=lambda lang: lang.isocode),
        )


@route("/upload/<prjname>/<lngname>", method="GET")
@protected(["upload", "prjname", "-"])
def page_get_subdir(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    linfo = language_info.isocode.get(lngname)
    if linfo is None:
        abort(404, "Language is unknown")
        return None
    return template("upload_lang_subdir", userauth=userauth, pmd=pmd, lnginfo=linfo)


@route("/upload/<prjname>/<lngname>", method="POST")
@protected(["upload", "prjname", "-"])
def page_post_subdir(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    linfo = language_info.isocode.get(lngname)
    if linfo is None:
        abort(404, "Language is unknown")
        return None

    langfile = request.files.langfile
    override = request.forms.override
    is_base = request.forms.base_language
    return handle_upload(userauth, pmd, prjname, langfile, override, is_base, linfo)


@route("/upload/<prjname>", method="POST")
@protected(["upload", "prjname", "-"])
def page_post(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata
    if not pdata.projtype.has_grflangid:
        abort(404, "No language identification provided.")
        return None

    langfile = request.files.langfile
    override = request.forms.override
    is_base = request.forms.base_language
    return handle_upload(userauth, pmd, prjname, langfile, override, is_base, None)


def handle_upload(userauth, pmd, projname, langfile, override, is_base, lng_data):
    """
    Process the upload.

    @param userauth: User authentication.
    @type  userauth: L{UserAuthentication}

    @param pmd: Project meta data.
    @type  pmd: L{ProjectMetaData}

    @param projname: Project name.
    @type  projname: C{str}

    @param langfile: Language file to load if available.
    @type  langfile: C{file} or C{None}

    @param override: Override existing text.
    @type  override: C{bool}

    @param lng_data: Used language, if provided.
    @type  lng_data: L{LanguageData} or C{None}
    """
    pdata = pmd.pdata

    # Missing language file in the upload.
    if not langfile or not langfile.file:
        abort(404, "Missing language file")
        return None

    base_language = pdata.get_base_language()

    # Cannot download a translation without base language.
    if not is_base and base_language is None:
        abort(404, "Project has no base language")
        return None

    # Read upload data
    text = langfile.file.read(config.cfg.language_file_size)
    if len(text) == config.cfg.language_file_size:
        abort(400, "Language file too large.")
        return None

    try:
        text = str(text, encoding="utf-8")
    except UnicodeDecodeError:
        abort(400, "Language file must be utf-8 encoded.")
        return None

    # Parse language file, and report any errors.
    ng_data = language_file.load_language_file(pdata.projtype, text, lng_data)
    if len(ng_data.errors) > 0:
        return template("upload_errors", userauth=userauth, pmd=pmd, errors=ng_data.errors)

    # Is the language allowed?
    if not pdata.projtype.allow_language(ng_data.language_data):
        abort(404, 'Language "{}" may not be uploaded'.format(ng_data.language_data.isocode))
        return None

    stamp = data.make_stamp()

    lng = pdata.languages.get(ng_data.language_data.isocode)
    if lng is None:  # New language being added.
        result = add_new_language(ng_data, pdata, is_base)
        if not result[0]:
            abort(404, result[0])
            return None
        lng = result[1]
        if is_base and base_language is None:
            base_language = lng

    if is_base:
        if base_language is not None and base_language != lng:
            abort(404, "Cannot change a translation to a base language")
            return None

        # Add strings as changes.
        for sv in ng_data.strings:
            sv.text = language_file.sanitize_text(sv.text)
            chgs = base_language.changes.get(sv.name)
            chg = get_blng_change(sv, base_language)
            if chg is None:  # New change.
                base_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, None, stamp, userauth.name, True)
                if chgs is None:
                    chgs = [chg]
                    base_language.changes[sv.name] = chgs
                else:
                    chgs.append(chg)
            else:
                # Only way to update a base language is by upload, no need for override check.
                chg.stamp = stamp
                chg.user = userauth.name

            for c in chgs:
                c.last_upload = c == chg

        # Update language properties as well.
        copy_lng_properties(pdata.projtype, ng_data, base_language)

        pdata.skeleton = ng_data.skeleton  # Use the new skeleton file.
        pdata.flush_related_cache()  # Drop the related strings cache.
        pdata.set_modified()

        # Push the new set of string-names to all languages (this includes the base language).
        str_names = set(sv.name for sv in ng_data.strings)
        for lang in pdata.languages.values():
            lng_modified = False
            not_seen = str_names.copy()
            for sn in list(lang.changes.keys()):
                not_seen.discard(sn)
                if sn in str_names:
                    continue  # Name is kept.
                del lang.changes[sn]  # Old string, delete
                lng_modified = True
            for sn in not_seen:
                # Missing translation are not saved, so no set_modified here.
                lang.changes[sn] = []

            if lng_modified:
                lang.set_modified()

    else:
        # Not a base language -> it is a translation.
        if base_language is not None and base_language == lng:
            abort(404, "Cannot change a base language to a translation")
            return None

        for sv in ng_data.strings:
            sv.text = language_file.sanitize_text(sv.text)

            # Find base language string for 'sv'.
            bchgs = base_language.changes.get(sv.name)
            if bchgs is None:
                continue  # Translation has a string not in the base language
            bchg = data.get_newest_change(bchgs, "")
            if bchg is None:
                continue  # Nothing to base against.
            base_text = bchg.base_text

            chgs = lng.changes.get(sv.name)
            chg = get_lng_change(sv, lng, base_text)
            if chg is None:  # It's a new text or new case.
                lng_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, lng_text, stamp, userauth.name, True)
                if chgs is None:
                    lng.changes[sv.name] = [chg]
                else:
                    chgs.append(chg)
            elif override:  # Override existing entry.
                chg.stamp = stamp
                chg.user = userauth.name

            # Set the change as the "last uploaded" one
            for c in chgs:
                c.last_upload = False

            chg.last_upload = True

        # Update language properties as well.
        copy_lng_properties(pdata.projtype, ng_data, lng)
        lng.set_modified()

    config.cache.save_pmd(pmd)

    if is_base:
        pmd.create_statistics(None)  # Update all languages.
    else:
        pmd.create_statistics(lng)

    message = "Successfully uploaded language '" + lng.name + "' " + utils.get_datetime_now_formatted()
    redirect("/project/<prjname>", prjname=projname, message=message)
    return None


def get_blng_change(sv, lng):
    """
    Get the best matching change in a base language for a given string value.
    (string and case should match, and the newest time stamp)

    @param sv: String value to match.
    @type  sv: L{StringValue}

    @param lng: Language to examine.
    @type  lng: L{Language}

    @return: The best change, if a matching change was found.
    @rtype:  C{None} or L{Change}
    """
    assert lng is not None
    chgs = lng.changes.get(sv.name)
    if chgs is None or len(chgs) == 0:
        return None

    best = None
    for chg in chgs:
        if sv.case != chg.case:
            continue
        if sv.text != chg.base_text.text:
            continue
        if best is None or best.stamp < chg.stamp:
            best = chg

    return best


def get_lng_change(sv, lng, base_text):
    """
    Get the best matching change in a language for a given string value.
    (string and case should match, and the newest time stamp)

    @param sv: String value to match.
    @type  sv: L{StringValue}

    @param lng: Language to examine.
    @type  lng: L{Language}

    @param base_text: Base text to match.
    @type  base_text: C{Text}

    @return: The best change, if a matching change was found.
    @rtype:  C{None} or L{Change}
    """
    assert lng is not None
    chgs = lng.changes.get(sv.name)
    if chgs is None or len(chgs) == 0:
        return None

    best, best_prio = None, 5  # Smaller prio is better.
    for chg in chgs:
        if sv.case != chg.case:
            continue
        if chg.new_text is None or sv.text != chg.new_text.text:
            continue

        # Calculate priority.
        if chg.base_text == base_text:
            new_prio = 1
        else:
            new_prio = 3

        if not chg.last_upload:
            new_prio = new_prio + 1

        if best is not None:
            if new_prio > best_prio:
                continue
            if new_prio == best_prio and best.stamp < chg.stamp:
                continue

        best, best_prio = chg, new_prio

    return best


def add_new_language(ng_data, pdata, base_lang):
    """
    Construct a new language, and add it to the project if it does not exist already.
    Returns the added language or an error description.

    @param ng_data: Loaded language file.
    @type  ng_data: L{NewGrfData}

    @param pdata: Project data.
    @type  pdata: L{Project}

    @param base_lang: Is the new language the base language?
    @type  base_lang: C{bool}

    @return: The language if it could be added, else C{None}.
    @rtype:  (C{True},L{Language}) or (C{False}, C{str})
    """
    if ng_data.language_data.isocode in pdata.languages:
        return (False, "Language {} already exists".format(ng_data.language_data.isocode))

    if pdata.base_language is None and not base_lang:  # We don't have a base language, and this is not one either.
        return (False, "Project has no base language yet, so translations are not possible")

    lng = data.Language(ng_data.language_data.isocode)
    lng.grflangid = ng_data.grflangid
    copy_lng_properties(pdata.projtype, ng_data, lng)
    lng.changes = {}
    pdata.languages[lng.name] = lng

    # Make it a base language if needed.
    if base_lang:
        pdata.base_language = lng.name
        pdata.skeleton = ng_data.skeleton
        pdata.flush_related_cache()

    # Add the current string names to the new language.
    for stp, sparam in pdata.skeleton:
        if stp == "string":
            lng.changes[sparam[1]] = []

    lng.set_modified()
    return (True, lng)


def copy_lng_properties(projtype, ng_data, lng):
    """
    Copy language properties from the loaded language file to the language.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param ng_data: Loaded language file.
    @type  ng_data: L{NewGrfData}

    @param lng: Language to update.
    @type  lng: L{Language}
    """
    lng.custom_pragmas = ng_data.custom_pragmas

    if ng_data.plural is not None:
        lng.plural = ng_data.plural
    else:
        lng.plural = lng.info.plural

    if not projtype.allow_gender:
        lng.gender = []
    elif ng_data.gender is not None:
        lng.gender = ng_data.gender
    else:
        lng.gender = lng.info.gender

    if not projtype.allow_case:
        lng.case = [""]
    elif ng_data.case is not None:
        lng.case = ng_data.case
    else:
        lng.case = lng.info.case

    lng.set_modified()
