"""
Upload a language file.
"""
from webtranslate.bottle import route, template, abort, request, redirect
from webtranslate.protect import protected
from webtranslate import config, data, utils
from webtranslate.newgrf import language_file

@route('/upload/<proj_name>', method = 'GET')
@protected(['upload', 'proj_name', '-'])
def page_get(proj_name):
    proj = config.cache.projects.get(proj_name)
    if proj is None:
        abort(404, "Page not found")
        return
    return template('upload_lang', proj_name = proj_name)

@route('/upload/<proj_name>', method = 'POST')
@protected(['upload', 'proj_name', '-'])
def page_post(proj_name):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    assert pdata is not None

    langfile    = request.files.langfile
    override    = request.forms.override
    is_base     = request.forms.base_language

    # Missing language file in the upload.
    if not langfile or not langfile.file:
        abort(404, "Missing language file")
        return

    base_language = pdata.get_base_language()

    # Cannot download a translation without base language.
    if not is_base and base_language is None:
        abort(404, "Project has no base language")
        return

    # Parse language file, and report any errors.
    errors = []
    ng_data = language_file.load_language_file(langfile.file, config.cfg.language_file_size, errors)
    if len(errors) > 0:
        return template('upload_errors', proj_name = proj_name, errors = errors)

    user = None # XXX Get user
    stamp = data.make_stamp()

    lng = pdata.languages.get(ng_data.language_data.isocode)
    if lng is None: # New language being added.
        result = add_new_language(ng_data, pdata, is_base)
        if not result[0]:
            abort(404, result[0])
            return
        lng = result[1]
        if is_base and base_language is None: base_language = lng

    if is_base:
        if base_language is not None and base_language != lng:
            abort(404, "Cannot change a translation to a base language")
            return

        # Add strings as changes.
        for sv in ng_data.strings:
            chg = get_best_change(sv, base_language, None, False)
            if chg is None: # New change.
                base_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, None, stamp, user)
                chgs = base_language.changes.get(sv.name)
                if chgs is None:
                     base_language.changes[sv.name] = [chg]
                else:
                    chgs.append(chg)
            else:
                if override: # Don't mind other changes at all.
                    chg.stamp = sv.stamp
                    chg.user = sv.user


        pdata.skeleton = ng_data.skeleton # Use the new skeleton file.

        # Push the new set of string-names to all languages (this includes the base language).
        str_names = set(sv.name for sv in ng_data.strings)
        for lng in pdata.languages.values():
            not_seen = str_names.copy()
            for sn in list(lng.changes.keys()):
                not_seen.discard(sn)
                if sn in str_names: continue # Name is kept.
                del lng.changes[sn] # Old string, delete
            for sn in not_seen:
                lng.changes[sn] = []


    else:
        # Not a base language -> it is a translation.
        if base_language is not None and base_language == lng:
            abort(404, "Cannot change a base language to a translation")
            return

        for sv in ng_data.strings:
            chgs = base_language.changes.get(sv.name)
            if chgs is None: continue # Translation has a string not in the base language
            chg = data.get_newest_change(chgs, '')
            if chg is None: continue # Nothing to base against.
            base_text = chg.base_text
            lng_chg  = get_best_change(sv, lng, base_text, True)
            if lng_chg is None: # It's a new text or new case.
                lng_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, lng_text, stamp, user)
                chgs = lng.changes.get(sv.name)
                if chgs is None:
                    lng.changes[sv.name] = [chg]
                else:
                    chgs.append(chg)
            elif override: # Override existing entry.
                lng_chg.stamp = stamp
                lng_chg.user = user

    # XXX remove old changes

    config.cache.save_pmd(pmd)
    pmd.create_statistics(None) # Update all languages.

    message = "Successfully uploaded language '" + lng.name +"' " + utils.get_datetime_now_formatted()
    redirect("/project/" + proj_name + '?message=' + message)


def get_best_change(sv, lng, base_text, search_new):
    """
    Get the best matching change in a language for a given string value.
    (string and case should match, and the newest time stamp)

    @param sv: String value to match.
    @type  sv: L{StringValue}

    @param lng: Language to examine.
    @type  lng: L{Language}

    @param base_text: Base text to match (if set).
    @type  base_text: C{None} or C{Text}

    @param search_new: If set, search the 'new_text' field, else search the 'base_text' field of the changes.
    @type  search_new: C{bool}

    @return: The best change, if a matching change was found.
    @rtype:  C{None} or L{Change}
    """
    assert lng is not None
    chgs = lng.changes.get(sv.name)
    if chgs is None or len(chgs) == 0: return None

    best = None
    for chg in chgs:
        if sv.case != chg.case: continue

        if search_new:
            if base_text is not None and chg.base_text != base_text: continue
            if chg.new_text is None or sv.text != chg.new_text.text: continue
        else:
            if sv.text != chg.base_text.text: continue

        if best is None or best.stamp < chg.stamp: best = chg

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

    if pdata.base_language is None and not base_lang: # We don't have a base language, and this is not one either.
        return (False, "Project has no base language yet, so translations are not possible")

    lng = data.Language(ng_data.language_data.isocode)
    lng.grflangid = ng_data.grflangid
    lng.plural = ng_data.plural
    lng.gender = ng_data.gender
    lng.case   = ng_data.case
    lng.changes = {}
    pdata.languages[lng.name] = lng

    # Make it a base language if needed.
    if base_lang:
        pdata.base_language = lng.name
        pdata.skeleton = ng_data.skeleton

    # Add the current string names to the new language.
    for stp, sparam in pdata.skeleton:
        if stp == 'string': lng.changes[sparam] = []

    return (True, lng)

