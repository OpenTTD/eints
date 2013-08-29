"""
Get the rights of users.

Special user roles:
 - SOMEONE:    Unauthenticated user
 - OWNER:      Owner of a project
 - TRANSLATOR: Translator of a language in a project
 - *:          Always matches
"""
import re, configparser

class UserRightRule:
    """
    @ivar user: User name or role.
    @type user: C{str}

    @ivar path: Path (four segments) of the rule.
    @type path: C{list} of C{str}

    @ivar grant_access: If set, give access when this rule matches, else deny access.
    @type grant_access: C{bool}
    """
    def __init__(self, user, path, grant_access):
        self.user = user
        self.path = path
        self.grant_access = grant_access

    def __str__(self):
        s = self.user
        if self.grant_access:
            s = s + " + /"
        else:
            s = s + " - /"
        return s + "/".join(self.path)

    def _update_entries(self, accesses, main_keys, other_keys, value):
        """
        Update the entry in L{main_keys} and if L{value} holds, also in L{other_keys}.

        @param accesses: Found access due to matched rules until now.
        @type  accesses: Mapping of user types to C{None} (unknown), C{False} (no), or C{True} (yes)

        @param main_keys: Entries to set unconditionally if not set already.
        @type  main_keys: C{list} of user types.

        @param other_keys: Entries to set if access is allowed.
        @param other_keys: C{list} of user types.

        @param value: Access value to set.
        @type  value: C{bool}
        """
        for k in main_keys:
            if accesses[k] is None:
                accesses[k] = value

        if value == True:
            for k in other_keys:
                if accesses[k] is None:
                    accesses[k] = value

    def update_matches(self, user, accesses):
        """
        Update the match information of the user types by this rule.

        @param user: Name of the user.
        @type  user: C{str}

        @param accesses: User information of all user types.
        @type  accesses: Mapping of user types to C{None} (unknown), C{False} (no), or C{True} (yes)

        @precond: The path of this rule matches.
        """
        if self.user == "*":
            self._update_entries(accesses, [user, "OWNER", "TRANSLATOR", "SOMEONE"], [], self.grant_access)
        elif self.user == 'SOMEONE':
            self._update_entries(accesses, ['SOMEONE'], [user, "OWNER", "TRANSLATOR"], self.grant_access)
        elif self.user == 'TRANSLATOR':
            self._update_entries(accesses, ['TRANSLATOR'], ["OWNER"], self.grant_access)
        elif self.user == 'OWNER':
            self._update_entries(accesses, ["OWNER"], [], self.grant_access)
        elif user == self.user and user != "unknown":
            self._update_entries(accesses, [user], [], self.grant_access)


    def match_path(self, path):
        """
        Does the given path match with the stored path?

        @param path: Path of a page in the application.
        @type  path: C{str}

        @return: Whether the path matches (possibly with wildcards).
        @rtype:  C{bool}
        """
        if len(path) != len(self.path): return False
        for p, sp in zip(path, self.path):
            if p == sp or sp == '*': continue
            return False
        return True


# Table with rights.
_table = []

FILENAME = "rights.dat"

def init_page_access():
    """
    Initialize the user rights table.
    """
    global _table

    _table = []
    rights_pat = re.compile('\\s*(\\S+)\\s+([-+])\\s+/([^/]+)/([^/]+)/([^/]+)/([^/]+)\\s*$')
    handle = open(FILENAME, "r", encoding = "utf-8")
    for idx, line in enumerate(handle):
        line = line.rstrip()
        if len(line) == 0 or line[0] == '#': continue
        m = rights_pat.match(line)
        if not m:
            print("Warning: Line {:d} ignored of {}".format(idx + 1, FILENAME))
            continue
        user = m.group(1)
        grant_access = (m.group(2) == '+')
        path = [m.group(3), m.group(4), m.group(5), m.group(6)]
        _table.append(UserRightRule(user, path, grant_access))

    handle.close()

# Table with project user data.
# Mapping of project names to mapping of roles to users.
# C{dict} of C{str} to C{dict} of C{str} to C{set} of C{str}
_projects = {}

PROJECTSFILE = "projects.dat"

def init_projects():
    """
    Initialize the projects table (mapping of projects to mapping of roles to users).
    """
    global _projects

    # Read projects user data.
    cfg = configparser.ConfigParser()
    cfg.read(PROJECTSFILE)
    _projects = {}
    for pn in cfg.sections():
        ps = cfg[pn]
        values = {}
        for k, ns in ps.items():
            names = set()
            for ns2 in ns.split(','):
                for ns3 in ns2.split(' '):
                    ns3 = ns3.strip()
                    if len(ns3) < 3: continue # User names are longer-equal to 3 characters.
                    names.add(ns3)
            values[k] = names
        _projects[pn] = values

def get_accesses(page, user):
    """
    Get access rights for all user types.

    @param page: Page name being accessed.
    @type  page: C{list} of C{str}

    @param user: User name (login name or 'unknown').
    @type  user: C{str}

    @return: User information of all user types.
    @rtype:  Mapping of user types to C{None} or C{False} (no), or C{True} (yes)
    """
    global _table

    # Mapping of all user types to status.
    # Value 'None' means unknown, 'False' means no, 'True' means yes.
    if user != "unknown":
        user_access = None
    else:
        user_access = False
    accesses = {user : user_access, "SOMEONE" : None, "OWNER" : None, "TRANSLATOR" : None}
    for urr in _table:
        if not urr.match_path(page): continue
        urr.update_matches(user, accesses)
    return accesses

def reduce_roles(accesses, prjname, lngname, user):
    """
    Verify roles of the user in the project, and adapt roles in L{accesses}.

    @param accesses: User information of all user types.
    @type  accesses: Mapping of user types to C{None} (unknown), C{False} (no), or C{True} (yes)

    @param prjname: Name of the project, if available.
    @type  prjname: C{str} or C{None}

    @param lngname: Name of the language, if available.
    @type  lngname: C{str} or C{None}

    @param user: User name (login name or 'unknown').
    @type  user: C{str}
    """
    global _projects

    if user == "unknown" or prjname is None or prjname not in _projects:
        accesses["OWNER"] = False
        accesses["TRANSLATOR"] = False
        return

    p = _projects[prjname]
    if 'owner' not in p or user not in p['owner']:
        accesses["OWNER"] = False
    if lngname not in p or user not in p[lngname]:
        accesses["TRANSLATOR"] = False

def has_access(accesses):
    """
    Is access allowed based on the previous computations?

    @param accesses: User information of all user types.
    @type  accesses: Mapping of user types to C{None} (unknown), C{False} (no), or C{True} (yes)

    @return: Whether access is allowed (C{True} means access is allowed).
    @rtype:  C{bool}
    """
    for v in accesses.values():
        if v == True: return True
    return False

def may_access(page, prjname, lngname, user):
    """
    May the given user be given access?

    @param page: Page name being accessed.
    @type  page: C{list} of C{str}

    @param prjname: Name of the project, if available.
    @type  prjname: C{str} or C{None}

    @param lngname: Name of the language, if available.
    @type  lngname: C{str} or C{None}

    @param user: User name (login name or 'unknown').
    @type  user: C{str}

    @return: Whether access is allowed (C{True} means access is allowed).
    @rtype:  C{bool}
    """
    accesses = get_accesses(page, user)
    reduce_roles(accesses, prjname, lngname, user)
    return has_access(accesses)
