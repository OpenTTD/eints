"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Called once to initialize the user system.
- get_authentication(user, pwd) -> C{UserAuthentication} to query permissions.
"""

from webtranslate.users import development, redmine, github, ldap

get_authentication = None
oauth_redirect = None
oauth_callback = None


def init(auth):
    """
    Setup authentication.
    """
    global get_authentication, oauth_redirect, oauth_callback

    if auth == "development":
        get_authentication = development.get_authentication
        development.init()
    elif auth == "redmine":
        get_authentication = redmine.get_authentication
        redmine.init()
    elif auth == "github":
        oauth_redirect = github.oauth_redirect
        oauth_callback = github.oauth_callback
        github.init()
    elif auth == "ldap":
        get_authentication = ldap.get_authentication
        ldap.init()
