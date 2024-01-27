"""
User authentication and authorization via github teams.

"""

import logging
import requests
import requests_oauthlib

from oauthlib.oauth2 import AccessDeniedError

from .. import (
    rights,
    userauth,
)

log = logging.getLogger(__name__)


github_organization = None
github_org_api_token = None
github_oauth_client_id = None
github_oauth_client_secret = None
github_api_url = None
github_url = None


def request_teams(name):
    """
    Request all teams an user is member of.

    @param name: Github login
    @type  name: C{str}

    @return: Teams
    @rtype:  C{set} of C{str}
    """

    if not github_organization or not github_org_api_token:
        return set()

    try:
        query = """
        query($org:String!, $user:String!) {
            organization(login: $org) {
                teams(first: 100, userLogins: [$user]) {
                    nodes {
                        name
                    }
                }
            }
        }
        """

        variables = {"org": github_organization, "user": name}
        r = requests.post(
            f"{github_api_url}/graphql",
            headers={"Authorization": "bearer " + github_org_api_token},
            json={"query": query, "variables": variables},
        )
        if r.status_code != 200:
            raise RuntimeError("HTTP request returned status {}".format(r.status_code))

        r = r.json()
        teams = set(t["name"] for t in r["data"]["organization"]["teams"]["nodes"])
        return teams
    except Exception:
        log.exception("Failed to request teams for user %s", name)
        return set()


class GithubUserAuthentication(userauth.UserAuthentication):
    """
    Implementation of UserAuthentication for Github authentication system.
    """

    def __init__(self):
        super(GithubUserAuthentication, self).__init__(False, "unknown")
        self.teams = set()
        self.userid = None
        self.state = None
        self.redirect = None

    def start_oauth(self, req_redirect, req_login):
        self.redirect = req_redirect
        oauth = requests_oauthlib.OAuth2Session(github_oauth_client_id)
        if req_login is not None:
            url, self.state = oauth.authorization_url("https://github.com/login/oauth/authorize", login=req_login)
        else:
            url, self.state = oauth.authorization_url("https://github.com/login/oauth/authorize")
        return url

    def callback(self, request_url):
        if self.is_auth or self.state is None:
            return None

        try:
            oauth = requests_oauthlib.OAuth2Session(github_oauth_client_id, state=self.state)
            self.state = None  # single use, forget now

            oauth.fetch_token(
                f"{github_url}/login/oauth/access_token",
                client_secret=github_oauth_client_secret,
                authorization_response=request_url,
            )
            if oauth.authorized:
                info = oauth.get(f"{github_api_url}/user").json()

                self.name = info["login"]  # can be changed, and reassigned to someone else
                self.userid = int(info["id"])  # persistent

                # All necessary data is available, now the user is considered authorized
                self.is_auth = True
                self.teams = request_teams(self.name)

                return self.redirect
        except AccessDeniedError:
            # The user denied access to our application; that is fine, just
            # don't log the user in and show him an error (which is exactly
            # what happens if we do absolutely nothing)
            pass
        except Exception:
            log.exception("Failed to get user information")

        return None

    def get_roles(self, prjname, lngname):
        eints_roles = set()
        if self.is_auth:
            eints_roles.add("USER")

            if lngname is not None and lngname in self.teams:
                eints_roles.add("TRANSLATOR")

        return eints_roles


def init():
    """
    Initialize the user admin system.
    """
    rights.init_page_access()


def oauth_redirect(req_redirect=None, req_login=None):
    """
    Redirect for authentication.

    @param req_redirect: Return URL
    @type  req_redirect: C{str} or C{None}

    @param req_login: Prefilled login name
    @type  req_login: C{str} or C{None}

    @return: Tuple of (Session, Redirect URL)
    @rtype:  (C{userauth.UserAuthentication}, C{str})
    """
    userauth = GithubUserAuthentication()
    return (userauth, userauth.start_oauth(req_redirect, req_login))


def oauth_callback(userauth, request_url):
    """
    Callback for authentication.

    @param userauth: Authentication session.
    @type  userauth: C{userauth.UserAuthentication}

    @param request_url: Complete URL of callback request.
    @type  request_url: C{str}

    @return: Redirect URL
    @rtype:  C{str} or C{None}
    """
    if isinstance(userauth, GithubUserAuthentication):
        # Valid session, check authentication
        return userauth.callback(request_url)
    else:
        # No session. Maybe user went back to /oauth2 after logout.
        return None
