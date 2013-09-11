"""
User administration system to use during development.

In particular the user management is very poor.
"""
from webtranslate import rights, userauth
from webtranslate.users import silly

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
    silly.init()
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
    if user is None or pwd is None or not silly.authenticate(user, pwd):
        return DevelopmentUserAuthentication(False, "unknown")
    else:
        return DevelopmentUserAuthentication(True, user)
