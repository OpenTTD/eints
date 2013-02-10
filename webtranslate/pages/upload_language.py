"""
Upload a language file.
"""
from webtranslate.bottle import route, template, abort, request
from webtranslate.protect import protected
from webtranslate import config, data
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

    langfile      = request.files.langfile
    is_existing   = request.forms.is_existing
    override      = request.forms.override
    base_language = request.forms.base_language

    if not base_language and pdata.base_language is None:
        abort(404, "Project has no base language")
        return

    if not langfile or not langfile.file:
        abort(404, "Missing language file")
        return
    # parse language file.
    errors = []
    ng_data = language_file.load_language_file(langfile.file, config.cfg.language_file_size, errors)

    if len(errors) > 0:
        return template('upload_errors', proj_name = proj_name, errors = errors)

    user = None # XXX Get user
    stamp = data.make_stamp()
    # XXX Implement the other cases as well.
    assert base_language
    assert not is_existing
    assert override

    if ng_data.language_data.isocode not in pdata.languages:
        # Adding a new language.
        result = add_new_language(ng_data, pdata, base_language)
        if not result[0]:
            abort(404, result[0])
            return
        lng = result[1]

    else:
        # Updating a language
        pass # XXX Remove old stuff

    if base_language:
        # Add strings as changes.
        for sv in ng_data.strings:
            base_text = data.Text(sv.text, sv.case, stamp)
            chg = data.Change(sv.name, sv.case, base_text, None, stamp, user)
            chgs = lng.changes.get(chg.string_name)
            if chgs is None:
                lng.changes[chg.string_name] = [chg]
            else:
                found = None
                for c in chgs:
                    if c.case == chg.case and c.base_text == chg.base_text:
                        found = c # String already present.
                        break
                if found is not None: # Found a duplicate.
                    if override: # Don't mind other changes at all.
                        found.stamp = chg.stamp
                        found.user = chg.user
                    continue

                chgs.append(chg)
                continue

        # XXX Incorporate loaded data in other files too.

    else:
        # Add strings as a translation.
        pass
        # XXX

    config.cache.save_pmd(pmd)
    return template('upload_ok', proj_name = proj_name)


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
    lng.cases  = ng_data.case
    lng.changes = {}
    pdata.languages[lng.name] = lng

    # Make it a base language if needed.
    if base_language:
        pdata.base_language = lng.name
        pdata.skeleton = ng_data.skeleton

    return (True, lng)

