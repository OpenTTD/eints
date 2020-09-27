"""
User administration system to use during development.

In particular the user management is very poor.
"""
import configparser
import logging
import os

from .. import (
    rights,
    userauth,
)

log = logging.getLogger(__name__)

# Table with user names and plain text passwords.
_users = None

FILENAME = "users.dat"


def init_users():
    """
    Initialize the user authentication system.
    """
    global _users

    _users = set()
    if not os.path.isfile(FILENAME):
        return

    handle = open(FILENAME, "r", encoding="utf-8")
    for line in handle:
        line = line.rstrip()
        if len(line) == 0 or line[0] == "#":
            continue
        i = line.find(":")
        if i < 0:
            continue
        j = line.find(":", i + 1)
        if j < 0:
            j = len(line)
        uname, pwd = line[:i].strip(), line[i + 1 : j]

        if len(uname) == 0 or len(pwd) == 0:
            continue
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

    if len(pwd) == 0:
        return False
    return (user, pwd) in _users


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
    cfg.optionxform = lambda option: option  # Don't convert keys to lowercase.
    cfg.read(PROJECTSFILE)
    _projects = {}
    for pn in cfg.sections():
        ps = cfg[pn]
        values = {}
        for k, ns in ps.items():
            names = set()
            for ns2 in ns.split(","):
                for ns3 in ns2.split(" "):
                    ns3 = ns3.strip()
                    if len(ns3) < 3:
                        # User names should be longer-equal to 3 characters.
                        log.error("Username %s ignored (too short)", ns3)
                        continue
                    names.add(ns3)
            values[k] = names
        _projects[pn] = values


class DevelopmentUserAuthentication(userauth.UserAuthentication):
    """
    Implementation of UserAuthentication for Development authentication system.
    """

    def __init__(self, is_auth, name):
        super(DevelopmentUserAuthentication, self).__init__(is_auth, name)

    def get_roles(self, prjname, lngname):
        eints_roles = set()
        if self.is_auth:
            eints_roles.add("USER")

            prj_owners = None
            prj_translators = None

            if prjname is not None:
                prj_roles = _projects.get(prjname)
                if prj_roles is not None:
                    prj_owners = prj_roles.get("owner")
                    if lngname is not None:
                        prj_translators = prj_roles.get(lngname)

            if prj_owners is not None and self.name in prj_owners:
                eints_roles.add("OWNER")

            if prj_translators is not None and self.name in prj_translators:
                eints_roles.add("TRANSLATOR")

        return eints_roles


def init():
    """
    Initialize the user admin system.
    """
    init_users()
    init_projects()
    rights.init_page_access()


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
