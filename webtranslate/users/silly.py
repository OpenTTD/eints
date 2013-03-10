"""
User authentication, the **EXTREMELY** simple way.
"""
import os

_users = None

FILENAME = "users.dat"

def init():
    """
    Initialize the user authentication system.
    """
    global _users

    _users = set()
    if not os.path.isfile(FILENAME): return

    handle = open(FILENAME, "r")
    for line in handle:
        line = line.rstrip()
        if len(line) == 0 or line[0] == '#': continue
        i = line.find(':')
        if i < 0: continue
        j = line.find(':', i + 1)
        if j < 0: continue
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
