import random

from .. import (
    config,
    data,
    utils,
)
from ..bottle import (
    abort,
    request,
    route,
)
from ..newgrf import (
    language_file,
    language_info,
)
from ..protect import protected
from ..utils import (
    redirect,
    template,
)

# Priorities of strings that need editing. Smaller number is more important to do first.
MISSING_PRIO = 1
INVALID_PRIO = 2
OUTDATED_PRIO = 3


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
    @type errors: C{list} of L{ErrorMessage}

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
            if user is None:
                user = "unknown"
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
            self.user = "none"
            self.trans_base = self.current_base
            txt = data.Text("", "", None)  # This breaks assumptions on the Text class.
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
        if self.case == "":
            return sname
        return sname + "." + self.case

    def __repr__(self):
        return "TransLationCase({}, {}, {})".format(repr(self.case), repr(self.transl), repr(self.related))


class StringAvoidanceCache:
    """
    LRU cache of string names to avoid picking.

    @cvar AVOID_MAXLEN: Maximum number of strings to store in the cache.
    @type AVOID_MAXLEN: C{int}

    @ivar cache: Cached items (string names to avoid).
    @type cache: C{dict} of C{str} to C{int}
    """

    AVOID_MAXLEN = 5

    def __init__(self):
        self.cache = {}

    def add(self, name):
        """
        Add a string to the cache.

        @param name: Name to add.
        @type  name: C{str}
        """
        i = self.cache.get(name)
        if i == 0:
            return

        new_cache = {name: 0}
        for nm, idx in self.cache.items():
            if i is None or idx < i:
                new_idx = idx + 1
                if new_idx < self.AVOID_MAXLEN:
                    new_cache[nm] = new_idx
            elif idx > i:
                new_cache[nm] = idx

        self.cache = new_cache

    def find(self, name):
        """
        Find the provided name in the cache.

        @param name: Name to find.
        @type  name: C{str}

        @return: Index of the entry if found, else C{None}
        @rtype:  C{int} or C{None}
        """
        return self.cache.get(name)


def find_string(pmd, lngname):
    """
    Find a string to translate.
    Collects the strings with the highest priority (the smallest number), and picks one at random.

    @param pmd: Project meta data.
    @type  pmd: L{ProjectMetaData}

    @param lngname: Language name.
    @type  lngname: C{str}

    @return: Name of a string with a highest priority (lowest prio number), if available.
    @rtype:  C{str} or C{None}
    """
    pdata = pmd.pdata
    blng = pdata.get_base_language()
    if blng is None:
        return None  # No strings to translate without base language.
    ldict = pdata.statistics.get(lngname)
    if ldict is None:
        return None  # Unsupported language.

    str_lists = {}
    str_lists[MISSING_PRIO] = []
    str_lists[INVALID_PRIO] = []
    str_lists[OUTDATED_PRIO] = []

    prio_map = {
        data.MISSING: str_lists[MISSING_PRIO],
        data.INVALID: str_lists[INVALID_PRIO],
        data.OUT_OF_DATE: str_lists[OUTDATED_PRIO],
    }

    # Collect all strings that need work in the above list(s).
    for sname in blng.changes:
        state = max(s[1] for s in pdata.statistics[lngname][sname])
        str_coll = prio_map.get(state)
        if str_coll is None:
            continue
        str_coll.append(sname)

    # Collect high priority strings, until we have enough, or we run out of strings.
    cur_strings = set()
    for _prio, strs in sorted(str_lists.items()):
        cur_strings.update(strs)
        if len(cur_strings) > StringAvoidanceCache.AVOID_MAXLEN:
            break  # Sounds like enough.

    if len(cur_strings) == 0:
        return None

    sac = pmd.string_avoid_cache.get(lngname)
    if sac is None:
        sac = StringAvoidanceCache()
        pmd.string_avoid_cache[lngname] = sac

    if len(cur_strings) > len(sac.cache):
        cur_strings.difference_update(sac.cache.keys())
        sel = random.choice(list(cur_strings))
        sac.add(sel)
        return sel
    else:
        # Just try them all, and pick the best one.
        best_val = None
        best_name = None
        for sname in cur_strings:
            idx = sac.find(sname)
            if idx is None:
                sac.add(sname)
                return sname
            if best_val is None or best_val < idx:
                best_val, best_name = idx, sname
        sac.add(best_name)
        return best_name


@route("/fix/<prjname>/<lngname>", method="GET")
@protected(["string", "prjname", "lngname"])
def fix_string(userauth, prjname, lngname):
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

    return fix_string_page(pmd, prjname, lngname, None)


def fix_string_page(pmd, prjname, lngname, message):
    """
    Jump to a string edit page to fix a string.

    @param pmd: Meta data of the project.
    @type  pmd: L{ProjectMetaData}

    @param prjname: Internal project identifier.
    @type  prjname: C{str}

    @param lngname: Language to select from.
    @type  lngname: C{str}

    @param message: Message to display, if any.
    @type  message: C{str} or C{None}
    """
    sname = find_string(pmd, lngname)
    if sname is None:
        if message is None:
            message = "All strings are up-to-date, perhaps some translations need rewording?"
        redirect("/translation/<prjname>/<lngname>", prjname=prjname, lngname=lngname, message=message)
        return

    if message is None:
        redirect("/string/<prjname>/<lngname>/<sname>", prjname=prjname, lngname=lngname, sname=sname)
    else:
        redirect("/string/<prjname>/<lngname>/<sname>", prjname=prjname, lngname=lngname, sname=sname, message=message)
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
    @rtype:  C{None} or tuple (L{ProjectMetaData}, L{Change}, L{Language}, L{StringInfo}
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
    assert pdata.projtype.allow_case or lng.case == [""]

    blng = pdata.get_base_language()
    if blng == lng:
        abort(404, "Language is not a translation")
        return None

    bchgs = blng.changes.get(sname)
    if bchgs is None or len(bchgs) == 0:
        abort(404, "String does not exist in the project")
        return None

    # Check newest base language string.
    bchg = max(bchgs)
    binfo = language_file.check_string(pdata.projtype, bchg.base_text.text, True, None, blng, True)
    if binfo.has_error:
        # XXX Add errors too
        abort(404, "String cannot be translated, its base language version is incorrect")
        return None

    return pmd, bchg, lng, binfo


def output_string_edit_page(
    userauth, bchg, binfo, lng, pmd, lngname, sname, states=None, message=None, message_class=None
):
    """
    Construct a page for editing a string.

    @param bchg: Last version of the base language.
    @type  bchg: L{Change}

    @param binfo: Information about the state of the L{bchg} string.
    @type  binfo: L{StringInfo}

    @param lng: Language being translated.
    @type  lng: L{Language}

    @param pmd: Project Meta Data.
    @type  pmd: L{ProjectMetaData}

    @param lngname: Language name.
    @type  lngname: C{str}


    @param sname: Name of the string.
    @type  sname: C{str}

    @param states: Changes, state and errors for (some of) the cases, omission of a case
                   means the function should derive it from the language.
    @type  states: C{dict} of C{str} to tuple (L{Change}, C{int}, C{list} of L{ErrorMessage}),
                   use C{None} to derive all.

    @return: Either an error, or an instantiated template.
    @rtype:  C{None} or C{str}
    """
    if states is None:
        states = {}
    pdata = pmd.pdata
    projtype = pdata.projtype

    # Mapping of case to list of related strings.
    related_cases = dict((case, []) for case in lng.case)
    for rel_sname in pdata.get_related_strings(sname):
        rel_chgs = lng.changes.get(rel_sname)
        if rel_chgs is not None:
            rel_chgs = data.get_all_newest_changes(rel_chgs, lng.case)
            for case, chg in rel_chgs.items():
                if chg is not None and chg.new_text is not None:
                    rc = related_cases.get(case)
                    if rc is not None:
                        rc.append(RelatedString(rel_sname, chg.new_text))

    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, None)
    now = data.make_stamp()

    transl_cases = []
    for case in lng.case:
        tranls = []

        cchgs = [(cchg, True) for cchg in case_chgs[case]]  # Tuples (case-change, 'saved translation')
        chg_err_state = states.get(case)
        if chg_err_state is not None:
            cchgs.append((chg_err_state[0], False))
        if len(cchgs) == 0:
            # No changes for this case, make a dummy one to display the base data.
            tra = Translation(bchg, None, now, False)
            if case == "":
                tra.errors = [language_file.ErrorMessage(language_file.ERROR, None, "String is missing")]
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
                        state, errors = data.get_string_status(projtype, lchg, case, lng, bchg.base_text, binfo)

                    tra.errors = errors
                    tra.state = data.STATE_MAP[state].name
                else:
                    # For older translations, the errors and state are never displayed.
                    tra.errors = []
                    tra.state = data.STATE_MAP[data.MISSING_OK].name

                tranls.append(tra)

        if projtype.allow_case or case == "":
            transl_cases.append(TransLationCase(case, tranls, related_cases[case]))

    related_languages = []
    if lng.name[:3] != pdata.base_language[:3]:
        for n, l in pdata.languages.items():
            if n[:3] != lng.name[:3] or n == lng.name:
                continue

            related = data.get_newest_change(lng.changes.get(sname), "")
            if related is not None:
                related_languages.append((l, related))
    related_languages.sort(key=lambda x: x[0].name)

    return template(
        "string_form",
        userauth=userauth,
        pmd=pmd,
        lng=lng,
        sname=sname,
        plurals=language_info.all_plurals[lng.plural].description,
        genders=lng.gender,
        cases=lng.case,
        related_languages=related_languages,
        tcs=transl_cases,
        message=message,
        message_class=message_class,
    )


@route("/string/<prjname>/<lngname>/<sname>", method="GET")
@protected(["string", "prjname", "lngname"])
def str_form(userauth, prjname, lngname, sname):
    parms = check_page_parameters(prjname, lngname, sname)
    if parms is None:
        return None

    pmd, bchg, lng, binfo = parms
    return output_string_edit_page(userauth, bchg, binfo, lng, pmd, lngname, sname, None)


@route("/string/<prjname>/<lngname>/<sname>", method="POST")
@protected(["string", "prjname", "lngname"])
def str_post(userauth, prjname, lngname, sname):
    parms = check_page_parameters(prjname, lngname, sname)
    if parms is None:
        return None

    pmd, bchg, lng, binfo = parms

    request.forms.recode_unicode = False  # Allow Unicode input
    request_forms = request.forms.decode()  # Convert dict to Unicode.

    base_str = request_forms.get("base")  # Base text translated against in the form.
    if base_str is None or base_str != bchg.base_text.text:
        abort(404, "Base language has been changed, please translate the newer version instead")
        return None

    # Get changes against bchg
    case_chgs = data.get_all_changes(lng.changes.get(sname), lng.case, bchg)
    projtype = pmd.pdata.projtype

    stamp = None  # Assigned a stamp object when a change is made in the translation.

    # Collected output data
    new_changes = []
    new_state_errors = {}

    for case in lng.case:
        trl_str = request_forms.get("text_" + case)  # Translation text in the form.
        if trl_str is None:
            continue  # It's missing from the form data.

        trl_str = language_file.sanitize_text(trl_str)
        if case == "" and trl_str == "" and bchg.base_text != "":
            # Empty base case for a non-empty string, was the "allow empty base translation" flag set?
            if request_forms.get("allow_empty_default") != "on":
                if stamp is None:
                    stamp = data.make_stamp()
                txt = data.Text(trl_str, case, stamp)
                tchg = data.Change(sname, case, bchg.base_text, txt, stamp, userauth.name)
                error = language_file.ErrorMessage(
                    language_file.ERROR,
                    None,
                    "Empty default case is not allowed (enable by setting 'Allow empty input').",
                )
                new_state_errors[case] = (tchg, data.INVALID, [error])
                continue

        # Check whether there is a match with a change in the translation.
        trl_chg = None
        for cchg in case_chgs[case]:
            if cchg.new_text.text == trl_str:
                trl_chg = cchg
                break

        if trl_chg is None:
            if case != "" and trl_str == "" and len(case_chgs[case]) == 0:
                continue  # Skip adding empty non-base cases if there are no strings.

            # A new translation against bchg!
            if stamp is None:
                stamp = data.make_stamp()
            txt = data.Text(trl_str, case, stamp)
            tchg = data.Change(sname, case, bchg.base_text, txt, stamp, userauth.name)
            state, errors = data.get_string_status(projtype, tchg, case, lng, bchg.base_text, binfo)
            if state == data.MISSING or state == data.INVALID:
                new_state_errors[case] = (tchg, state, errors)
            else:
                new_changes.append(tchg)

            continue

        # Found a match with an existing translation text
        if case_chgs[case][-1] == trl_chg:
            # Latest translation.
            if trl_chg.base_text == bchg.base_text:  # And also the latest base language!
                continue
            state, _errors = data.get_string_status(projtype, trl_chg, case, lng, bchg.base_text, binfo)
            if state == data.OUT_OF_DATE:
                # We displayed a 'this string is correct' checkbox. Was it changed?
                if request_forms.get("ok_" + case):
                    # Move to latest base language text.
                    if stamp is None:
                        stamp = data.make_stamp()
                    trl_chg.base_text = bchg.base_text
                    trl_chg.stamp = stamp
                    trl_chg.user = userauth.name
            continue

        # We got an older translation instead.
        if stamp is None:
            stamp = data.make_stamp()
        tchg = data.Change(sname, case, bchg.base_text, trl_chg.new_text, stamp, userauth.name)
        state, errors = data.get_string_status(projtype, tchg, case, lng, bchg.base_text, binfo)
        if state == data.MISSING or state == data.INVALID:
            new_state_errors[case] = (tchg, state, errors)
        else:
            new_changes.append(tchg)

        continue  # Not really needed.

    if len(new_state_errors) > 0:
        return output_string_edit_page(
            userauth,
            bchg,
            binfo,
            lng,
            pmd,
            lngname,
            sname,
            new_state_errors,
            message="There were error(s)",
            message_class="error",
        )

    # No errors, store the changes.
    for tchg in new_changes:
        if sname in lng.changes:
            lng.changes[sname].append(tchg)
        else:
            lng.changes[sname] = [tchg]
        lng.set_modified()

    modified = config.process_project_changes(pmd.pdata)  # Update changes of the project.
    if modified or stamp is not None:
        config.cache.save_pmd(pmd)
        pmd.create_statistics(lng)

    # Construct a message that the string is changed.
    if len(new_changes) > 0:
        message = "Successfully updated string '" + sname + "' " + utils.get_datetime_now_formatted()
    else:
        message = None
    return fix_string_page(pmd, prjname, lngname, message)
