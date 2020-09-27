"""
Get the rights of users.

Special user roles:
 - SOMEONE:    Unauthenticated user
 - USER:       Authenticated user
 - OWNER:      Owner of a project
 - TRANSLATOR: Translator of a language in a project
 - *:          Always matches
"""
import logging
import re

log = logging.getLogger(__name__)


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

    def eval(self, roles):
        """
        Evaluate this rule.

        @param roles: Set of roles.
        @type  roles: C{set} of C{str}

        @return: Whether this rule decides access, and its decision.
        @rtype:  C{bool} or C{None}

        @precond: The path of this rule matches.
        """
        if (self.user == "*") or (self.user in roles):
            return self.grant_access
        else:
            return None

    def match_path(self, path):
        """
        Does the given path match with the stored path?

        @param path: Path of a page in the application.
        @type  path: C{str}

        @return: Whether the path matches (possibly with wildcards).
        @rtype:  C{bool}
        """
        if len(path) != len(self.path):
            return False
        for p, sp in zip(path, self.path):
            if p == sp or sp == "*":
                continue
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
    rights_pat = re.compile("\\s*(\\S+)\\s+([-+])\\s+/([^/]+)/([^/]+)/([^/]+)/([^/]+)\\s*$")
    handle = open(FILENAME, "r", encoding="utf-8")
    for idx, line in enumerate(handle):
        line = line.rstrip()
        if len(line) == 0 or line[0] == "#":
            continue
        m = rights_pat.match(line)
        if not m:
            log.warning("Line %d ignored of %s", idx + 1, FILENAME)
            continue
        user = m.group(1)
        grant_access = m.group(2) == "+"
        path = [m.group(3), m.group(4), m.group(5), m.group(6)]
        _table.append(UserRightRule(user, path, grant_access))

    handle.close()


def has_access(page, roles):
    """
    Test access to a page for a user with a set of roles.

    @param page: Page name being accessed.
    @type  page: C{list} of C{str}

    @param roles: Set of roles
    @type  roles: C{set} of C{str}

    @return: Whether access is granted.
    @rtype:  C{bool}
    """
    global _table

    if "USER" not in roles:
        roles = set(["SOMEONE"])

    for urr in _table:
        if not urr.match_path(page):
            continue
        access = urr.eval(roles)
        if access is not None:
            return access

    # No match, just deny.
    return False
