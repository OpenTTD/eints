"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Called once to initialize the user system.
- may_access(user, pwd, pname, prjname, lngname) -> boolean May a user access a page?
"""

from webtranslate.users import development, redmine

may_access = None

def init(auth):
    """
    Setup authentication.
    """
    global may_access

    if auth == 'development':
        may_access = development.may_access
        development.init()
    elif auth == 'redmine':
        may_access = redmine.may_access
        redmine.init()

