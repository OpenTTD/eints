"""
Upload a language file.
"""
from webtranslate.bottle import route, template, abort, request
from webtranslate.protect import protected
from webtranslate import config, data
from webtranslate.newgrf import language_file

@route('/upload/<proj_name>', method = 'GET')
@protected(['upload', 'proj_name', '-'])
def page(proj_name):
    proj = config.cache.projects.get(proj_name)
    if proj is None:
        abort(404, "Page not found")
        return
    return template('upload_lang', proj_name = proj_name)

@route('/upload/<proj_name>', method = 'POST')
@protected(['upload', 'proj_name', '-'])
def page(proj_name):
    proj = config.cache.projects.get(proj_name)
    if proj is None:
        abort(404, "Page not found")
        return

    pdata = proj.pdata
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
    assert base_language and pdata.base_language is None
    assert not is_existing
    assert override

    if ng_data.language_data.isocode in pdata.languages:
        abort(404, "Language {} already exists".format(ng_data.language_data.isocode))
        return

    lng = data.Language(ng_data.language_data.isocode)
    lng.grflangid = ng_data.grflangid
    lng.plural = ng_data.plural
    lng.gender = ng_data.gender
    lng.cases  = ng_data.case
    lng.changes = {}

    assert len(pdata.languages) == 0 # XXX Incorporate loaded data in other files too otherwise.
    # Copy string changes into the language.
    for sv in ng_data.strings:
        chg = data.Change(sv.name, sv.case, sv.text, None, stamp, user)
        chgs = lng.changes.get(chg.string_name)
        if chgs is None:
            lng.changes[chg.string_name] = [chg]
        else:
            chgs.append(chg)

    pdata.languages[lng.name] = lng
    pdata.base_language = lng.name
    pdata.skeleton = ng_data.skeleton

    # XXX Save project!!
    return template('upload_ok', proj_name = proj_name)
