"""
User administration system to use during development.

In particular the user management is very poor.
"""
import os
from webtranslate import rights, userauth

# Table with user names and plain text passwords.
_users = None

FILENAME = "users.dat"

def init_users():
    """
    Initialize the user authentication system.
    """
    global _users

    _users = set()
    if not os.path.isfile(FILENAME): return

    handle = open(FILENAME, "r", encoding = "utf-8")
    for line in handle:
        line = line.rstrip()
        if len(line) == 0 or line[0] == '#': continue
        i = line.find(':')
        if i < 0: continue
        j = line.find(':', i + 1)
        if j < 0:
            j = len(line)
        uname, pwd = line[:i].strip(), line[i+1:j]

        if len(uname) == 0 or len(pwd) == 0: continue
        _users.add((uname, pwd))

    handle.close()

def authenticate(user, pwd):
    """
    Is the provided user and password combination valid?

    @param user: User name.
    @type  user: C{str}

    @param pwd: Password.
    @type  pwd: C{str}

    @return: Whether the combination is valid (C{True} means 'valid').
    @rtype:  C{bool}
    """
    global _users

    if len(pwd) == 0: return False
    return (user, pwd) in _users



class DevelopmentUserAuthentication(userauth.UserAuthentication):
    """
    Implementation of UserAuthentication for Development authentication system.
    """
    def __init__(self, is_auth, name):
        super(DevelopmentUserAuthentication, self).__init__(is_auth, name)

    def may_access(self, pname, prjname, lngname):
        return rights.may_access(pname, prjname, lngname, self.name)

def init():
    """
    Initialize the user admin system.
    """
    init_users()
    rights.init_page_access()
    rights.init_projects()

def get_authentication(user, pwd):
    """
    Authenticate a user and return an authentication object.

    @param user: Name of the user, if provided (external data).
    @type  user: C{str} or C{None}

    @param pwd: Password of the user, if provided (external data).
    @type  pwd: C{str} or C{None}

    @return: UserAuthentication object to test accesses with.
    @rtype: C{UserAuthentication}
    """
    if user is None or pwd is None or not authenticate(user, pwd):
        return DevelopmentUserAuthentication(False, "unknown")
    else:
        return DevelopmentUserAuthentication(True, user)
