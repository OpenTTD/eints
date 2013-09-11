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

    @ivar saved: Translation is saved in the project data (strings being edited but having errors are not saved).
    @type saved: C{bool}
    """
    def __init__(self, bchg, lchg, now, saved):
        """
        Constructor.

        @param bchg: Change in the base language, if available.
        @type  bchg: L{Change} or C{None}

        @param lchg: Change in the translation, if available.
        @type  lchg: L{Change} or C{None}

        @param now: The current moment in time, if available.
        @type  now: L{Stamp} or C{None}

        @param saved: Translation comes from the project data (instead of a result of a user editing the string).
        @type  saved: C{bool}
        """
        self.current_base = bchg.base_text
        self.state = None
        self.errors = []
        self.saved = saved

        if lchg is not None:
            user = lchg.user
            if user is None: user = "unknown"
            self.user = user
            self.trans_base = lchg.base_text
            self.text = lchg.new_text
            if saved:
                self.stamp_desc = utils.get_relative_time(lchg.stamp, now)
                self.stamp = str(lchg.stamp)
            else:
                self.stamp_desc = None
                self.stamp = None
        else:
            self.user = 'none'
            self.trans_base = self.current_base
            txt = data.Text('', '', None) # This breaks assumptions on the Text class.
            self.text = txt
            self.stamp_desc = None
            self.stamp = None

class RelatedString:
    """
    Related string of a translation. Case of the string is implicit, it is the same as the
    L{TransLationCase.case} field in the containing object.

    @ivar sname: Name of the string.
    @type sname: C{str}

    @ivar text: Current text of the related string.
    @type text: C{Text}
    """
    def __init__(self, sname, text):
        self.sname = sname
        self.text = text

class TransLationCase:
    """
    Class for storing things to display with a single case in the translation of a string.

    @ivar case: The case used for this object.
    @type case: C{str}

    @ivar transl: Previous translations, sorted from new to old.
    @type transl: C{list} of L{Translation}

    @ivar related: Related strings.
    @type related: C{list} of L{RelatedString}
    """
    def __init__(self, case, transl, related):
        self.case = case
        self.transl = transl
        self.related = related

    def get_stringname(self, sname):
        if self.case == '': return sname
        return sname + '.' + self.case

    def __repr__(self):
        return "TransLationCase({}, {}, {})".format(repr(self.case), repr(self.transl), repr(self.related))

def find_string(pmd, lngname, missing_prio, invalid_prio, outdated_prio):
    """
    Find a string to translate.
    Collects the strings with the highest priority (the smallest number), and picks one at random.

    @param pmd: Project meta data.
    @type  pmd: L{ProjectMetaData}

    @param lngname: Language name.
    @type  lngname: C{str}

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
    ldict = pdata.statistics.get(lngname)
    if ldict is None: return None # Unsupported language.

    prio_map = {data.MISSING: missing_prio,
                data.INVALID: invalid_prio,
                data.OUT_OF_DATE: outdated_prio}

    cur_prio = max(missing_prio, invalid_prio, outdated_prio) + 1
    cur_strings = []
    for sname in blng.changes:
        state = max(s[1] for s in pdata.statistics[lngname][sname])
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

@route('/fix/<prjname>/<lngname>', method = 'GET')
@protected(['string', 'prjname', 'lngname'])
def fix_string(user, prjname, lngname):
    """
    Fix a random string.

    @param prjname: Name of the project.
    @type  prjname: C{str}

    @param lngname: Language name.
    @type  lngname: C{str}
    """
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    blng = pdata.get_base_language()
    if blng == lng:
        abort(404, "Language is not a translation")
        return

    return fix_string_page(pmd, prjname, lngname, None)


def fix_string_page(pmd, prjname, lngname, message):
    sname = find_string(pmd, lngname, 1, 2, 3)
    if sname is None:
        if message is None: message = "All strings are up-to-date, perhaps some translations need rewording?"
        redirect('/translation/{}/{}?message={}'.format(prjname, lngname, message))
        return

    if message is None:
        redirect('/string/{}/{}/{}'.format(prjname, lngname, sname))
    else:
        redirect('/string/{}/{}/{}?message={}'.format(prjname, lngname, sname, message))
    return

def check_page_parameters(prjname, lngname, sname):
    """
    Check whether the parameters make any sense and abort if not, else return the derived project data.

    @param prjname: Name of the project.
    @type  prjname: C{str}

    @param lngname: Name of the language.
    @type  lngname: C{str}

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
    lng = pdata.languages.get(lngname)
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

def output_string_edit_page(bchg, binfo, lng, prjname, pdata, lngname, sname, states = None):
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

    @param lngname: Language name.
    @type  lngname: C{str}


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

    # Mapping of case to list of related strings.
    related_cases = dict((case, []) for case in lng.case)
    for rel_sname in pdata.get_related_strings(sname):
        rel_chgs = lng.changes.get(rel_sname)
        if rel_chgs is not None:
            rel_chgs = data.get_all_newest_changes(rel_chgs, lng.case)
            for case, chg in rel_chgs.items():
                if chg is not None and chg.new_text is not None:
                    related_cases[case].append(RelatedString(rel_sname, chg.new_text))


    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, None)
    now = data.make_stamp()

    transl_cases = []
    for case in lng.case:
        tranls = []

        cchgs = [(cchg, True) for cchg in case_chgs[case]] # Tuples (case-change, 'saved translation')
        chg_err_state = states.get(case)
        if chg_err_state is not None: cchgs.append((chg_err_state[0], False))
        if len(cchgs) == 0:
            # No changes for this case, make a dummy one to display the base data.
            tra = Translation(bchg, None, now, False)
            if case == '':
                tra.errors = [('ERROR', None, 'String is missing')]
                tra.state = data.STATE_MAP[data.MISSING].name
            else:
                tra.errors = []
                tra.state = data.STATE_MAP[data.MISSING_OK].name

            tranls.append(tra)

        else:
            # Changes do exist, add them (in reverse chronological order).
            cchgs.reverse()
            for idx, (lchg, saved) in enumerate(cchgs):
                tra = Translation(bchg, lchg, now, saved)
                if idx == 0:
                    # Newest string, add errors
                    if chg_err_state is not None:
                        state, errors = chg_err_state[1], chg_err_state[2]
                    else:
                        state, errors = data.get_string_status(lchg, case, lng, bchg.base_text, binfo)

                    tra.errors = errors
                    tra.state = data.STATE_MAP[state].name
                else:
                    # For older translations, the errors and state are never displayed.
                    tra.errors = []
                    tra.state = data.STATE_MAP[data.MISSING_OK].name

                tranls.append(tra)

        transl_cases.append(TransLationCase(case, tranls, related_cases[case]))

    transl_cases.sort(key=lambda tc: tc.case)
    return template('string_form', proj_name = prjname, pdata = pdata,
                    lname = lngname, sname = sname, tcs = transl_cases)


@route('/string/<prjname>/<lngname>/<sname>', method = 'GET')
@protected(['string', 'prjname', 'lngname'])
def str_form(user, prjname, lngname, sname):
    parms = check_page_parameters(prjname, lngname, sname)
    if parms is None: return

    pmd, bchg, lng, binfo = parms
    return output_string_edit_page(bchg, binfo, lng, prjname, pmd.pdata, lngname, sname, None)


@route('/string/<prjname>/<lngname>/<sname>', method = 'POST')
@protected(['string', 'prjname', 'lngname'])
def str_post(user, prjname, lngname, sname):
    parms = check_page_parameters(prjname, lngname, sname)
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

        trl_str = language_file.sanitize_text(trl_str)

        # Check whether there is a match with a change in the translation.
        trl_chg = None
        for cchg in case_chgs[case]:
            if cchg.new_text.text == trl_str:
                trl_chg = cchg
                break

        if trl_chg is None:
            if case != '' and trl_str == '' and len(case_chgs[case]) == 0:
                continue # Skip adding empty non-base cases if there are no strings.

            # A new translation against bchg!
            if stamp is None: stamp = data.make_stamp()
            txt = data.Text(trl_str, case, stamp)
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
        return output_string_edit_page(bchg, binfo, lng, prjname, pmd.pdata, lngname, sname,
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

    # Construct a message that the string is changed.
    if len(new_changes) > 0:
        message = "Successfully updated string '" + sname +"' " + utils.get_datetime_now_formatted()
    else:
        message = None
    return fix_string_page(pmd, prjname, lngname, message)
