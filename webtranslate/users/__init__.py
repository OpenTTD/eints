"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Called once to initialize the user system.
- get_authentication(user, pwd) -> C{UserAuthentication} to query permissions.
"""

from webtranslate.users import development, redmine

get_authentication = None

def init(auth):
    """
    Setup authentication.
    """
    global get_authentication

    if auth == 'development':
        get_authentication = development.get_authentication
        development.init()
    elif auth == 'redmine':
        get_authentication = redmine.get_authentication
        redmine.init()

