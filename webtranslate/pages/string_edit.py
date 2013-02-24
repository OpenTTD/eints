import random
from webtranslate.bottle import route, template, abort, request, redirect
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
            txt = data.Text('', '', None) # This breaks assumptions on the Text class.
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
        assert case is not None # XXX
        self.case = case
        self.transl = transl

    def get_stringname(self, sname):
        if self.case == '': return sname
        return sname + '.' + self.case

def find_string(pmd, lname, missing_prio, invalid_prio, outdated_prio):
    """
    Find a string to translate.
    Collects the strings with the highest priority (the smallest number), and picks one at random.

    @param pmd: Project meta data.
    @type  pmd: L{ProjectMetaData}

    @param lname: Language name.
    @type  lname: C{str}

    @param missing_prio: Priority of finding a missing string.
    @type  missing_prio: C{int}

    @param invalid_prio: Priority of finding an invalid string.
    @type  invalid_prio: C{int}

    @param outdated_prio: Priority of finding an outdated string.
    @type  outdated_prio: C{int}

    @return: Name of a string with a highest priority (lowest prio number), if available.
    @rtype:  C{str} or C{None}
    """
    pdata = pmd.pdata
    blng = pdata.get_base_language()
    if blng is None: return None # No strings to translate without base language.
    ldict = pdata.statistics.get(lname)
    if ldict is None: return None # Unsupported language.

    prio_map = {data.MISSING: missing_prio,
                data.INVALID: invalid_prio,
                data.OUT_OF_DATE: outdated_prio}

    cur_prio = max(missing_prio, invalid_prio, outdated_prio) + 1
    cur_strings = []
    for sname in blng.changes:
        state = max(s[1] for s in pdata.statistics[lname][sname])
        state_prio = prio_map.get(state)
        if state_prio is None: continue
        if state_prio == cur_prio:
            cur_strings.append(sname)
            continue
        if state_prio < cur_prio:
            cur_prio = state_prio
            cur_strings = [sname]
            continue

    if len(cur_strings) == 0: return None
    return random.choice(cur_strings)

@route('/fix/<proj_name>/<lname>', method = 'GET')
@protected(['string', 'proj_name', 'lname'])
def fix_string(proj_name, lname):
    """
    Fix a random string.

    @param proj_name: Name of the project.
    @type  proj_name: C{str}

    @param lname: Language name.
    @type  lname: C{str}
    """
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

    sname = find_string(pmd, lname, 1, 2, 3)
    if sname is None:
        message = "All strings are up-to-date, perhaps some translations need rewording?"
        redirect('/language/{}/{}?message={}'.format(proj_name, lname, message))
        return

    redirect('/string/{}/{}/{}'.format(proj_name, lname, sname))
    return


@route('/string/<proj_name>/<lname>/<sname>', method = 'GET')
@protected(['string', 'proj_name', 'lname'])
def str_form(proj_name, lname, sname):
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

    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, None)

    transl_cases = []
    assert '' in lng.case # XXX
    for case in lng.case:
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
            assert case is not None # XXX
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


@route('/string/<proj_name>/<lname>/<sname>', method = 'POST')
@protected(['string', 'proj_name', 'lname'])
def str_post(proj_name, lname, sname):
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

    base_str = request.forms.get('base') # Base text translated against in the form.
    if base_str is None or base_str != bchg.base_text.text:
        abort(404, "Base language has been changed, please translate the newer version instead")
        return

    # Get changes against bchg
    assert lng.case is not None # XXX
    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, bchg)

    user = None # XXX Fix user
    stamp = None # Assigned a stamp object when a change is made in the translation.

    assert '' in lng.case # XXX
    for case in lng.case:
        assert case is not None # XXX
        trl_str = request.forms.get('text_' + case) # Translation text in the form.
        if trl_str is None: continue # It's missing from the form data.
        # Check whether there is a match with a change in the translation.
        trl_chg = None
        for cchg in case_chgs[case]:
            if cchg.new_text.text == trl_str:
                trl_chg = cchg
                break
        if trl_chg is None:
            # A new translation against bchg!
            if stamp is None: stamp = data.make_stamp()
            txt = data.Text(trl_str, case, stamp)
            tchg = data.Change(sname, case, bchg.base_text, txt, stamp, user)
            if sname in lng.changes:
                lng.changes[sname].append(tchg)
            else:
                lng.changes[sname] = [tchg]

            continue
        # Found a match with an existing translation text
        if case_chgs[case][0] == trl_chg:
            # Latest translation.
            if trl_chg.base_text == bchg.base_text: # And also the latest base language!
                continue
            state, _errors = data.get_string_status(trl_chg, case, lng, bchg.base_text, binfo)
            if state == data.OUT_OF_DATE:
                # We displayed a 'this string is correct' checkbox. Was it changed?
                if request.forms.get('ok_' + case):
                    # Move to latest base language text.
                    if stamp is None: stamp = data.make_stamp()
                    trl_chg.base_text = bchg.base_text
                    trl_chg.stamp = stamp
                    trl_chg.user = user
            continue

        # We got an older translation instead.
        if stamp is None: stamp = data.make_stamp()
        tchg = data.Change(sname, case, trl_chg.base_text, trl_chg.new_text, stamp, user)
        if sname in lng.changes:
            lng.changes[sname].append(tchg)
        else:
            lng.changes[sname] = [tchg]

        continue # Not really needed.

    # XXX Remove old changes

    if stamp is not None:
        config.cache.save_pmd(pmd)
        pmd.create_statistics(lng)

    return "ok"
