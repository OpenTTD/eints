from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import data, config

class Translation:
    """
    All information of a translation.

    @ivar current_base: Current text of the base language.
    @type current_base: L{Text}

    @ivar trans_base: Base language text used in the translation.
    @type trans_base: L{Text}

    @ivar text: Text of current translation.
    @type text: L{Text}

    @ivar state: State of this translation, if available.
    @type state: C{str} or C{None}

    @ivar errors: Errors found in this translation, if available.
    @type errors: C{list} of C{tuple} (C{str}, C{None}, C{str})

    @ivar user: User that created the translation. C{None} means it is a fake change.
    @type user: C{str} or C{None}

    @ivar stamp: Time stamp of the translation.
    @type stamp: L{Stamp} or C{None}
    """
    def __init__(self, bchg, lchg):
        self.current_base = bchg.base_text
        self.state = None
        self.errors = []

        if lchg is not None:
            user = lchg.user
            if user is None: user = "unknown"
            self.user = user
            self.trans_base = lchg.base_text
            self.text = lchg.new_text
            self.stamp = lchg.stamp
        else:
            self.user = 'none'
            self.trans_base = self.current_base
            txt = data.Text('', None, None) # This breaks assumptions on the Text class.
            self.text = txt
            self.stamp = None


class TransLationCase:
    """
    Class for storing things to display with a single case in the translation of a string.

    @ivar case: The case used for this object.
    @type case: C{str}

    @ivar transl: Previous translations, sorted from new to old.
    @type transl: C{list} of L{Translation}
    """
    def __init__(self, case, transl):
        self.case = case
        self.transl = transl

    def get_stringname(self, sname):
        if self.case == '': return sname
        return sname + '.' + self.case


@route('/string/<proj_name>/<lname>/<sname>', method = 'GET')
@protected(['string', 'proj_name', 'lname'])
def project(proj_name, lname, sname):
    pmd = config.cache.get_pmd(proj_name)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    blng = pdata.get_base_language()
    if blng == lng:
        abort(404, "Language is not a translation")
        return

    bchgs = blng.changes.get(sname)
    if bchgs is None or len(bchgs) == 0:
        abort(404, "String does not exist in the project")
        return

    bchg = max(bchgs)
    binfo = data.get_base_string_info(bchg.base_text.text, blng)
    if binfo is None:
        # XXX Add errors too
        abort(404, "String cannot be translated, its base language version is incorrect")
        return

    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case)

    transl_cases = []
    for case in lng.case + ['']:
        tranls = []
        transl_cases.append(TransLationCase(case, tranls))

        cchgs = case_chgs[case]
        cchgs.reverse()
        for idx, lchg in enumerate(cchgs):
            tra = Translation(bchg, lchg)
            if idx == 0:
                state, errors = data.get_string_status(lchg, case, lng, bchg.base_text, binfo)
                tra.errors = errors
                tra.state = data.STATE_MAP[state]
            else:
                tra.errors = []
                tra.state = data.STATE_MAP[data.MISSING_OK]
            tranls.append(tra)

        if len(tranls) == 0:
            # No changes for this case, make a dummy one to display the base data.
            tra = Translation(bchg, None)
            tra.user = None
            if case == '':
                tra.errors = [('ERROR', None, 'String is missing')]
                tra.state = data.STATE_MAP[data.MISSING]
            else:
                tra.errors = []
                tra.state = data.STATE_MAP[data.MISSING_OK]

            tranls.append(tra)

    transl_cases.sort(key=lambda tc: tc.case)

    return template('string_form', proj_name = proj_name, pdata = pdata,
                    lname = lname, sname = sname, tcs = transl_cases)
