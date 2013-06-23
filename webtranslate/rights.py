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

    def match_user(self, user, prjname, lngname):
        """
        Does the given user name match with the user name stored in the rule?

        @param user: Name of the user, or 'unknown'.
        @type  user: C{str}

        @param prjname: Name of the project, if available.
        @type  prjname: C{str} or C{None}

        @param lngname: Name of the language, if available.
        @type  lngname: C{str} or C{None}

        @return: Whether the user matches.
        @rtype:  C{bool}
        """
        global _projects

        if self.user == '*':
            return True
        elif self.user == 'SOMEONE':
            return user == 'unknown'
        elif user == 'unknown': # 'unknown' users will never match below.
            return False
        elif self.user == 'OWNER':
            if prjname is None or prjname not in _projects: return False
            p = _projects[prjname]
            if 'owner' not in p or user not in p['owner']: return False
            return True
        elif self.user == 'TRANSLATOR':
            if prjname is None or lngname is None or prjname not in _projects: return False
            p = _projects[prjname]
            # Owners are also allowed access
            if 'owner' not in p or user not in p['owner']: return False
            if lngname not in p or user not in p[lngname]: return False
            return True
        else:
            return user == self.user

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
    handle = open(FILENAME, "r")
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
    """
    global _table
    for urr in _table:
        if not urr.match_path(page) or not urr.match_user(user, prjname, lngname): continue
        return urr.grant_access

    return False
