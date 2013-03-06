import random
from webtranslate.bottle import route, template, abort, request, redirect
from webtranslate.protect import protected
from webtranslate import data, config, utils
from webtranslate.newgrf import language_file

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

    @ivar stamp_desc: Short description of the time stamp.
    @type stamp_desc: C{str} or C{None}

    @ivar stamp: Time stamp of the translation.
    @type stamp: C{str} or C{None}
    """
    def __init__(self, bchg, lchg, now):
        """
        Constructor.

        @param bchg: Change in the base language, if available.
        @type  bchg: L{Change} or C{None}

        @param lchg: Change in the translation, if available.
        @type  lchg: L{Change} or C{None}

        @param now: The current moment in time, if available.
        @type  now: L{Stamp} or C{None}
        """
        self.current_base = bchg.base_text
        self.state = None
        self.errors = []

        if lchg is not None:
            user = lchg.user
            if user is None: user = "unknown"
            self.user = user
            self.trans_base = lchg.base_text
            self.text = lchg.new_text
            self.stamp_desc = utils.get_relative_time(lchg.stamp, now)
            self.stamp = str(lchg.stamp)
        else:
            self.user = 'none'
            self.trans_base = self.current_base
            txt = data.Text('', '', None) # This breaks assumptions on the Text class.
            self.text = txt
            self.stamp_desc = None
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

@route('/fix/<prjname>/<lname>', method = 'GET')
@protected(['string', 'prjname', 'lname'])
def fix_string(user, prjname, lname):
    """
    Fix a random string.

    @param prjname: Name of the project.
    @type  prjname: C{str}

    @param lname: Language name.
    @type  lname: C{str}
    """
    pmd = config.cache.get_pmd(prjname)
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

    return fix_string_page(pmd, prjname, lname)


def fix_string_page(pmd, prjname, lname):
    sname = find_string(pmd, lname, 1, 2, 3)
    if sname is None:
        message = "All strings are up-to-date, perhaps some translations need rewording?"
        redirect('/language/{}/{}?message={}'.format(prjname, lname, message))
        return

    redirect('/string/{}/{}/{}'.format(prjname, lname, sname))
    return

def check_page_parameters(prjname, lname, sname):
    """
    Check whether the parameters make any sense and abort if not, else return the derived project data.

    @param prjname: Name of the project.
    @type  prjname: C{str}

    @param lname: Name of the language.
    @type  lname: C{str}

    @param sname: Name of the string.
    @type  sname: C{str}

    @return: Nothing if the parameters don't make sense,
             else the project meta data, base change, language, and base text info.
    @rtype:  C{None} or tuple (L{ProjectMetaData}, L{Change}, L{Language}, L{NewGrfStringInfo}
    """
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return None

    pdata = pmd.pdata
    lng = pdata.languages.get(lname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return None

    blng = pdata.get_base_language()
    if blng == lng:
        abort(404, "Language is not a translation")
        return None

    bchgs = blng.changes.get(sname)
    if bchgs is None or len(bchgs) == 0:
        abort(404, "String does not exist in the project")
        return None

    bchg = max(bchgs)
    binfo = data.get_base_string_info(bchg.base_text.text, blng)
    if binfo is None:
        # XXX Add errors too
        abort(404, "String cannot be translated, its base language version is incorrect")
        return None

    return pmd, bchg, lng, binfo

def output_string_edit_page(bchg, binfo, lng, prjname, pdata, lname, sname, states = None):
    """
    Construct a page for editing a string.

    @param bchg: Last version of the base language.
    @type  bchg: L{Change}

    @param binfo: Information about the state of the L{bchg} string.
    @type  binfo: L{NewGrfStringInfo}

    @param lng: Language being translated.
    @type  lng: L{Language}


    @param prjname: System project name
    @type  prjname: C{str}

    @param pdata: Project data.
    @type  pdata: L{Project}

    @param lname: Language name.
    @type  lname: C{str}


    @param sname: Name of the string.
    @type  sname: C{str}

    @param states: Changes, state and errors for (some of) the cases, omission of a case
                   means the function should derive it from the language.
    @type  states: C{dict} of C{str} to tuple (L{Change}, C{int}, C{list} of tuples (C{str}, C{None}, C{str})),
                   use C{None} to derive all.

    @return: Either an error, or an instantiated template.
    @rtype:  C{None} or C{str}
    """
    if states is None: states = {}

    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, None)
    now = data.make_stamp()

    transl_cases = []
    for case in lng.case:
        tranls = []

        cchgs = case_chgs[case]
        chg_err_state = states.get(case)
        if chg_err_state is not None: cchgs.append(chg_err_state[0])
        if len(cchgs) == 0:
            # No changes for this case, make a dummy one to display the base data.
            tra = Translation(bchg, None, now)
            if case == '':
                tra.errors = [('ERROR', None, 'String is missing')]
                tra.state = data.STATE_MAP[data.MISSING]
            else:
                tra.errors = []
                tra.state = data.STATE_MAP[data.MISSING_OK]

            tranls.append(tra)

        else:
            # Changes do exist, add them (in reverse chronological order).
            cchgs.reverse()
            for idx, lchg in enumerate(cchgs):
                tra = Translation(bchg, lchg, now)
                if idx == 0:
                    # Newest string, add errors
                    if chg_err_state is not None:
                        state, errors = chg_err_state[1], chg_err_state[2]
                    else:
                        state, errors = data.get_string_status(lchg, case, lng, bchg.base_text, binfo)

                    tra.errors = errors
                    tra.state = data.STATE_MAP[state]
                else:
                    # For older translations, the errors and state are never displayed.
                    tra.errors = []
                    tra.state = data.STATE_MAP[data.MISSING_OK]

                tranls.append(tra)

        transl_cases.append(TransLationCase(case, tranls))

    transl_cases.sort(key=lambda tc: tc.case)
    return template('string_form', proj_name = prjname, pdata = pdata,
                    lname = lname, sname = sname, tcs = transl_cases)


@route('/string/<prjname>/<lname>/<sname>', method = 'GET')
@protected(['string', 'prjname', 'lname'])
def str_form(user, prjname, lname, sname):
    parms = check_page_parameters(prjname, lname, sname)
    if parms is None: return

    pmd, bchg, lng, binfo = parms
    return output_string_edit_page(bchg, binfo, lng, prjname, pmd.pdata, lname, sname, None)


@route('/string/<prjname>/<lname>/<sname>', method = 'POST')
@protected(['string', 'prjname', 'lname'])
def str_post(user, prjname, lname, sname):
    parms = check_page_parameters(prjname, lname, sname)
    if parms is None: return

    pmd, bchg, lng, binfo = parms

    request_forms = request.forms.decode() # Convert dict to Unicode.

    base_str = request_forms.get('base') # Base text translated against in the form.
    if base_str is None or base_str != bchg.base_text.text:
        abort(404, "Base language has been changed, please translate the newer version instead")
        return

    # Get changes against bchg
    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, bchg)

    stamp = None # Assigned a stamp object when a change is made in the translation.

    # Collected output data
    new_changes = []
    new_state_errors = {}

    for case in lng.case:
        trl_str = request_forms.get('text_' + case) # Translation text in the form.
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
            txt = language_file.sanitize_text(trl_str)
            txt = data.Text(txt, case, stamp)
            tchg = data.Change(sname, case, bchg.base_text, txt, stamp, user)
            state, errors = data.get_string_status(tchg, case, lng, bchg.base_text, binfo)
            if state == data.MISSING or state == data.INVALID:
                new_state_errors[case] = (tchg, state, errors)
            else:
                new_changes.append(tchg)

            continue

        # Found a match with an existing translation text
        if case_chgs[case][-1] == trl_chg:
            # Latest translation.
            if trl_chg.base_text == bchg.base_text: # And also the latest base language!
                continue
            state, _errors = data.get_string_status(trl_chg, case, lng, bchg.base_text, binfo)
            if state == data.OUT_OF_DATE:
                # We displayed a 'this string is correct' checkbox. Was it changed?
                if request.forms_get('ok_' + case):
                    # Move to latest base language text.
                    if stamp is None: stamp = data.make_stamp()
                    trl_chg.base_text = bchg.base_text
                    trl_chg.stamp = stamp
                    trl_chg.user = user
            continue

        # We got an older translation instead.
        if stamp is None: stamp = data.make_stamp()
        tchg = data.Change(sname, case, bchg.base_text, trl_chg.new_text, stamp, user)
        state, errors = data.get_string_status(tchg, case, lng, bchg.base_text, binfo)
        if state == data.MISSING or state == data.INVALID:
            new_state_errors[case] = (tchg, state, errors)
        else:
            new_changes.append(tchg)

        continue # Not really needed.

    if len(new_state_errors) > 0:
        request.query['message'] = 'There were error(s)' # XXX Needs a better solution (pass message obj to template?)
        request.query['message_class'] = 'error'
        return output_string_edit_page(bchg, binfo, lng, prjname, pmd.pdata, lname, sname,
                                       new_state_errors)

    # No errors, store the changes.
    for tchg in new_changes:
        if sname in lng.changes:
            lng.changes[sname].append(tchg)
        else:
            lng.changes[sname] = [tchg]

    modified = config.process_project_changes(pmd.pdata) # Update changes of the project.
    if modified or stamp is not None:
        config.cache.save_pmd(pmd)
        pmd.create_statistics(lng)

    return fix_string_page(pmd, prjname, lname)
