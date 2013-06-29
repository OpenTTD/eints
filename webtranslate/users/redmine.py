"""
User and webpage management handled by RedMine (http://www.redmine.org/).

The owner and translators of the rights are mapped to roles in RedMine through
the C{<redmine/>} section in the config file.
"""

# Also initialized in the config loader.
db_type = None
db_schema = None
db_name = None
db_password = None
db_user = None
db_host = None
db_port = None

owner_role = None
translator_roles = {} # Mapping of iso language name to role name.

def init():
    """
    Initialize the user admin system.
    """
    pass

def may_access(user, pwd, pname, prjname, lngname):
    """
    May a user access a page?

    @param user: Name of the user, if provided (external data).
    @type  user: C{str} or C{None}

    @param pwd: Password of the user, if provided (external data).
    @type  pwd: C{str} or C{None}

    @param pname: Page name being accessed.
    @type  pname: C{list} of C{str}

    @param prjname: Project name of the page, if any.
    @type  prjname: C{str} or C{None}

    @param lngname: Language name of the page, if any.
    @type  lngname: C{str} or C{None}

    @return: Whether the user may access the page.
    @rtype:  C{bool}
    """
    return False

