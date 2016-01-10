"""
Upload a language file.
"""
from webtranslate.bottle import route, template, abort, request, redirect
from webtranslate.protect import protected
from webtranslate import config, data, utils
from webtranslate.newgrf import language_file, language_info

@route('/upload/<prjname>', method = 'GET')
@protected(['upload', 'prjname', '-'])
def page_get(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    if pdata.projtype.has_grflangid:
        return template('upload_lang', pmd = pmd)
    else:
        return template('upload_lang_select', pmd = pmd,
                    lnginfos = sorted(pdata.get_all_languages(), lambda l: l.isocode))

@route('/upload/<prjname>/<lngname>', method = 'GET')
@protected(['upload', 'prjname', '-'])
def page_get_subdir(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    linfo = language_info.isocode.get(lngname)
    if linfo is None:
        abort(404, "Language is unknown")
        return
    return template('upload_lang_subdir', pmd = pmd, lnginfo = linfo)

@route('/upload/<prjname>/<lngname>', method = 'POST')
@protected(['upload', 'prjname', '-'])
def page_post_subdir(userauth, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    linfo = language_info.isocode.get(lngname)
    if linfo is None:
        abort(404, "Language is unknown")
        return

    langfile = request.files.langfile
    override = request.forms.override
    is_base  = request.forms.base_language
    return handle_upload(userauth, pmd, prjname, langfile, override, is_base, linfo)

@route('/upload/<prjname>', method = 'POST')
@protected(['upload', 'prjname', '-'])
def page_post(userauth, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    if not pdata.projtype.has_grflangid:
        abort(404, "No language identification provided.")
        return

    langfile = request.files.langfile
    override = request.forms.override
    is_base  = request.forms.base_language
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
        return

    base_language = pdata.get_base_language()

    # Cannot download a translation without base language.
    if not is_base and base_language is None:
        abort(404, "Project has no base language")
        return

    # Parse language file, and report any errors.
    ng_data = language_file.load_language_file(pdata.projtype, langfile.file, config.cfg.language_file_size, lng_data)
    if len(ng_data.errors) > 0:
        return template('upload_errors', pmd = pmd, errors = ng_data.errors)

    # Is the language allowed?
    if not pdata.projtype.allow_language(ng_data.language_data):
        abort(404, "Language \"{}\" may not be uploaded".format(ng_data.language_data.isocode))
        return

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
            sv.text = language_file.sanitize_text(sv.text)
            chg = get_blng_change(sv, base_language)
            if chg is None: # New change.
                base_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, None, stamp, userauth.name, True)
                chgs = base_language.changes.get(sv.name)
                if chgs is None:
                    base_language.changes[sv.name] = [chg]
                else:
                    for c in chgs:
                        c.last_upload = False
                    chgs.append(chg)
            else:
                if override: # Don't mind other changes at all.
                    chg.stamp = stamp
                    chg.user = userauth.name

        # Update language properties as well.
        copy_lng_properties(ng_data, base_language)

        pdata.skeleton = ng_data.skeleton # Use the new skeleton file.
        pdata.flush_related_cache() # Drop the related strings cache.
        pdata.set_modified()

        # Push the new set of string-names to all languages (this includes the base language).
        str_names = set(sv.name for sv in ng_data.strings)
        for lang in pdata.languages.values():
            lng_modified = False
            not_seen = str_names.copy()
            for sn in list(lang.changes.keys()):
                not_seen.discard(sn)
                if sn in str_names: continue # Name is kept.
                del lang.changes[sn] # Old string, delete
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
            return

        for sv in ng_data.strings:
            sv.text = language_file.sanitize_text(sv.text)

            # Find base language string for 'sv'.
            bchgs = base_language.changes.get(sv.name)
            if bchgs is None: continue # Translation has a string not in the base language
            chg = data.get_newest_change(bchgs, '')
            if chg is None: continue # Nothing to base against.
            base_text = chg.base_text

            lng_chg  = get_lng_change(sv, lng, base_text)
            if lng_chg is None: # It's a new text or new case.
                lng_text = data.Text(sv.text, sv.case, stamp)
                chg = data.Change(sv.name, sv.case, base_text, lng_text, stamp, userauth.name, True)
                chgs = lng.changes.get(sv.name)
                if chgs is None:
                    lng.changes[sv.name] = [chg]
                else:
                    for c in chgs:
                        c.last_upload = False
                    chgs.append(chg)
            elif override: # Override existing entry.
                lng_chg.stamp = stamp
                lng_chg.user = userauth.name

        # Update language properties as well.
        copy_lng_properties(ng_data, lng)
        lng.set_modified()

    config.cache.save_pmd(pmd)

    if is_base:
        pmd.create_statistics(None) # Update all languages.
    else:
        pmd.create_statistics(lng)

    message = "Successfully uploaded language '" + lng.name +"' " + utils.get_datetime_now_formatted()
    redirect("/project/" + projname + '?message=' + message)


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
    if chgs is None or len(chgs) == 0: return None

    best = None
    for chg in chgs:
        if sv.case != chg.case: continue
        if sv.text != chg.base_text.text: continue
        if best is None or best.stamp < chg.stamp: best = chg

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
    if chgs is None or len(chgs) == 0: return None

    best, best_prio = None, 5 # Smaller prio is better.
    for chg in chgs:
        if sv.case != chg.case: continue
        if chg.new_text is None or sv.text != chg.new_text.text: continue

        # Calculate priority.
        if chg.base_text == base_text:
            new_prio = 1
        else:
            new_prio = 3

        if not chg.last_upload: new_prio = new_prio + 1

        if best is not None:
            if new_prio > best_prio: continue
            if new_prio == best_prio and best.stamp < chg.stamp: continue

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

    if pdata.base_language is None and not base_lang: # We don't have a base language, and this is not one either.
        return (False, "Project has no base language yet, so translations are not possible")

    lng = data.Language(ng_data.language_data.isocode)
    lng.grflangid = ng_data.grflangid
    copy_lng_properties(ng_data, lng)
    lng.changes = {}
    pdata.languages[lng.name] = lng

    # Make it a base language if needed.
    if base_lang:
        pdata.base_language = lng.name
        pdata.skeleton = ng_data.skeleton
        pdata.flush_related_cache()

    # Add the current string names to the new language.
    for stp, sparam in pdata.skeleton:
        if stp == 'string': lng.changes[sparam[1]] = []

    lng.set_modified()
    return (True, lng)

def copy_lng_properties(ng_data, lng):
    """
    Copy language properties from the loaded language file to the language.

    @param ng_data: Loaded language file.
    @type  ng_data: L{NewGrfData}

    @param lng: Language to update.
    @type  lng: L{Language}
    """
    lng.custom_pragmas = ng_data.custom_pragmas
    lng.plural = ng_data.plural
    lng.gender = ng_data.gender
    lng.case   = ng_data.case
    lng.set_modified()

