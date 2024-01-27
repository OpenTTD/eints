"""
Login/logout
"""

from urllib.parse import quote

from .. import utils, users
from ..bottle import (
    redirect,
    request,
    route,
)
from ..protect import (
    abort,
    protected,
    start_session,
    stop_session,
)


def login_success(r):
    if r is None or not r.startswith("/"):
        r = "/userprofile"

    redirect(r + "?message=" + quote("Login successful!"))


@route("/login", method="GET")
@protected(["login", "-", "-"])
def login(userauth):
    req_redirect = request.query.get("redirect")
    req_login = request.query.get("login")

    if userauth.is_auth:
        login_success(req_redirect)
    elif users.oauth_redirect:
        session, url = users.oauth_redirect(req_redirect, req_login)
        start_session(session)
        redirect(url)
    elif users.get_authentication:
        return utils.template("login", userauth=userauth, req_login=req_login, req_redirect=req_redirect)
    else:
        abort(500, "No authentication method")
    return None


@route("/login", method="POST")
@protected(["login", "-", "-"])
def login_post(userauth):
    if not users.get_authentication:
        abort(500, "No authentication method")
        return None

    req_redirect = request.forms.get("redirect")
    req_login = request.forms.get("login")
    req_password = request.forms.get("password")

    if req_login and req_password:
        userauth = users.get_authentication(req_login, req_password)
        if userauth.is_auth:
            start_session(userauth)
            login_success(req_redirect)
            return None

    return utils.template(
        "login",
        userauth=userauth,
        req_login=req_login,
        req_redirect=req_redirect,
        message="GitHub authentication failed; please try again",
        message_class="error",
    )


@route("/oauth2", method="GET")
@protected(["oauth2", "-", "-"])
def oauth(userauth):
    if not users.oauth_callback:
        abort(500, "No authentication method")
        return

    req_redirect = users.oauth_callback(userauth, request.url)
    if userauth.is_auth:
        login_success(req_redirect)
    else:
        utils.redirect("/", message="GitHub authentication failed; please try again", message_class="error")


@route("/logout", method="GET")
def logout():
    stop_session()
    utils.redirect("/", message="Logout successful!")
