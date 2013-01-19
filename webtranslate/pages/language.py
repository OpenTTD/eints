from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import users, projects

class LanguageEntry:
    """
    Entry that displays the properties of a string.

    @ivar name: Name of the string.
    @type name: C{str}

    @ivar state: State of the string.
    @type state: C{int} (0=master, 1=up-to-date, 2=out-of-date, 3=missing)

    @ivar text: Text of the string.
    @type text: C{str}
    """
    def __init__(self, name, state, text):
        self.name = name
        self.state = state
        self.text = text


@route('/languages/<name>/<lname>', method = 'GET')
@protected(['language', 'name', 'lname'])
def project(name, lname):
    proj = projects.projects.projects.get(name)
    if proj is None:
        abort(404, "Page not found")
        return

    if lname not in proj.languages:
        abort(404, "Page not found")
        return

    lng = proj.load_strings(lname)
    if lng is None:
        abort(404, "Page not found")
        return

    entries = []
    if lng.strings is not None:
        if lng.master_lang is None:
            # Displaying an untranslated language.
            for entry in sorted(lng.strings.texts.items()):
                entries.append(LanguageEntry(entry[0], 0, entry[1].master.text))
        else:
            # Displaying a translated language.
            for sname, sval in sorted(lng.strings.texts.items()):
                if sval.text is None:
                    # Untranslated string
                    text = "(Not available)"
                    state = 3
                else:
                    text = sval.text.text
                    state = 1
                    if sval.master is not None and \
                            sval.text.time_stamp < sval.master.time_stamp:
                        state = 2
                entries.append(LanguageEntry(sname, state, text))

    return template('language', name = name, lname = lname, entries = entries)
