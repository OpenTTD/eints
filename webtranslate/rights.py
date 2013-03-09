"""
Get the rights of users.

Special user roles:
- SOMEONE:    Unauthenticated user
- OWNER:      Owner of a project
- TRANSLATOR: Translator of a language in a project
- *:          Always matches
"""
import re

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

    def match_user(self, user):
        """
        Does the given user name match with the user name stored in the rule?

        @param user: Name of the user, or 'unknown'.
        @type  user: C{str}

        @return: Whether the user matches.
        @rtype:  C{bool}
        """
        if self.user == '*':
            return True
        elif self.user == 'SOMEONE':
            return user == 'unknown'
        elif user == 'unknown':
            return False
        elif self.user == 'OWNER':
            return False # XXX
        elif self.user == 'TRANSLATOR':
            return False # XXX
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
            if p == sp: continue
            if p != '-' and sp == '*': continue
            return False
        return True


# Table with rights.
_table = []


FILENAME = "rights.dat"

rights_pat = re.compile('\\s*(\\S+)\\s+([-+])\\s+/([^/]+)/([^/]+)/([^/]+)/([^/]+)\\s*$')

def init():
    """
    Initialize the user rights table.
    """
    global _table

    _table = []
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


def may_access(page, user):
    """
    May the given user be given access?

    @param page: Page name being accessed.
    @type  page: C{list} of C{str}

    @param user: User name (login name or 'unknown').
    @type  user: C{str}
    """
    global _table
    for urr in _table:
        if not urr.match_path(page) or not urr.match_user(user): continue
        return urr.grant_access

    return False
