"""
Download a language file.
"""
from webtranslate.bottle import route, template, abort, response
from webtranslate.protect import protected
from webtranslate import config, data

@route('/download/<proj_name>/<language>', method = 'GET')
@protected(['download', 'proj_name', 'language'])
def download(user, proj_name, language):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Page not found")
        return

    pdata = pmd.pdata
    base_lng = pdata.get_base_language()

    lng = pdata.languages.get(language)
    if lng is None:
        abort(404, "Language does not exist")
        return

    response.content_type = 'text/plain; charset=UTF-8'
    lines = []
    for skel_type, skel_value in pdata.skeleton:
        if skel_type == 'literal':
            lines.append(skel_value)
            continue
        if skel_type == 'string':
            column, sname = skel_value
            chgs = lng.changes.get(sname)
            if chgs is not None:
                for case in lng.case:
                    chg = data.get_newest_change(chgs, case)
                    if chg is not None:
                        if case == '':
                            line = sname
                        else:
                            line = sname + "." + case

                        if lng == base_lng:
                            text = chg.base_text.text
                        else:
                            text = chg.new_text.text

                        length = column - len(line)
                        if length < 1: length = 1
                        lines.append(line + (' ' * length) + ':' + text)
            continue

        if skel_type == 'grflangid':
            lines.append('##grflangid 0x{:02x}'.format(lng.grflangid))
            continue

        if skel_type == 'plural':
            lines.append('##plural {:d}'.format(lng.plural))
            continue

        if skel_type == 'case':
            cases = [c for c in lng.case if c != '']
            if len(cases) > 0:
                lines.append('##case ' + ' '.join(cases))
            continue

        if skel_type == 'gender':
            if len(lng.gender) > 0:
                lines.append('##gender ' + ' '.join(lng.gender))
            continue

    return '\n'.join(lines)
