from webtranslate.bottle import route, template, abort
from webtranslate.protect import protected
from webtranslate import data, config

class CaseDisplayData:
    """
    All data to display a single case of a string.

    @ivar case: Case of the string.
    @type case: C{str}

    @ivar state: State of the case.
    @type state: C{str}

    @ivar text: Text of the string.
    @type text: C{str}
    """
    def __init__(self, case, state, text):
        self.case = case
        self.state = state
        self.text = text

    def get_str_casename(self, sname):
        if self.case == '': return sname
        return sname + "." + self.case

class StringDisplayData:
    """
    All data of a string to display in the language overview.

    @ivar sname: Name of the string.
    @type sname: C{str}

    @ivar cases: Cases, sorted on case name.
    @type cases: C{list} of L{CaseDisplayData}
    """
    def __init__(self, sname, base):
        self.sname = sname
        self.base = base
        self.cases = []

    def __lt__(self, other):
        if not isinstance(other, StringDisplayData): return False
        return self.sname < other.sname

    def __eq__(self, other):
        if not isinstance(other, StringDisplayData): return False
        return self.sname == other.sname


@route('/translation/<prjname>/<lngname>', method = 'GET')
@protected(['translation', 'prjname', 'lngname'])
def project(user, prjname, lngname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Project does not exist")
        return

    pdata = pmd.pdata
    lng = pdata.languages.get(lngname)
    if lng is None:
        abort(404, "Language does not exist in the project")
        return

    blng = pdata.get_base_language() # As above we established there is at least one language, this should work.
    stored = [[], [], [], [], []] # unknown, up-to-date, out-of-date, invalid, missing
    sdict = pdata.statistics
    sdict = sdict.get(lngname) # Statistics dict for the queried language.
    if sdict is None:
        abort(404, "Missing language statistics")
        return

    unknown = data.UNKNOWN
    for sname, bchgs in blng.changes.items():
        cstates = sdict[sname]
        state = max(s[1] for s in cstates)
        if state >= unknown:
            bchg = data.get_newest_change(bchgs, '')
            sdd = StringDisplayData(sname, bchg.base_text.text)
            chgs = lng.changes.get(sname)
            if chgs is not None:
                cases = data.get_all_newest_changes(chgs, lng.case)
                for case, cstate in cstates:
                    chg = cases[case]
                    if chg is not None:
                        if lng is blng:
                            text = chg.base_text.text
                        else:
                            text = chg.new_text.text
                            if text == '' and case != '':
                                # Suppress empty non-default case from translations.
                                continue
                        cdd = CaseDisplayData(case, data.STATE_MAP[cstate].name, text)
                        sdd.cases.append(cdd)

            stored[state - unknown].append(sdd)

    strings = []
    for i, strs in enumerate(stored, start = unknown):
        strs.sort()
        title = data.STATE_MAP[i].name
        strings.append((title, strs))
    return template('translation', proj_name = prjname, is_blng = (lng == blng),
                    pdata = pdata, language = lngname, strings = strings)
