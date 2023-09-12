"""
Bottle authentication decorator.
"""
import datetime
import secrets

from . import (
    config,
    userauth,
)
from .bottle import (
    abort,
    request,
    response,
)
from .utils import redirect


class ScriptAuth(userauth.UserAuthentication):
    """
    Authentication used by sync-script on localhost
    """

    def __init__(self):
        super().__init__(True, "translators")
        self.roles = {"USER", "OWNER"}

    def get_roles(self, prjname, lngname):
        return self.roles


_script_auth = ScriptAuth()
translators_password = None

_sessions = dict()
SESSION_COOKIE = "eints_sid"
MAX_SESSION_AGE = datetime.timedelta(hours=16)
LOGIN_TIMEOUT = datetime.timedelta(minutes=10)


def cleanup_sessions():
    now = datetime.datetime.utcnow()
    for sid, session in list(_sessions.items()):
        if not session.is_auth and now > session.login_timeout:
            del _sessions[sid]
        elif now > session.expires:
            del _sessions[sid]


def start_session(userauth):
    cleanup_sessions()

    userauth.sid = secrets.token_hex(32)
    userauth.expires = datetime.datetime.utcnow() + MAX_SESSION_AGE
    userauth.login_timeout = datetime.datetime.utcnow() + LOGIN_TIMEOUT
    _sessions[userauth.sid] = userauth
    response.set_cookie(SESSION_COOKIE, userauth.sid, expires=userauth.expires, httponly=True)


def get_session():
    sid = request.get_cookie(SESSION_COOKIE)
    if sid is not None:
        session = _sessions.get(sid)
        if session is not None:
            if datetime.datetime.utcnow() < session.expires:
                return session
            else:
                stop_session()
    return userauth.UserAuthentication(False, "unknown")


def stop_session():
    sid = request.get_cookie(SESSION_COOKIE)
    if sid is not None and sid in _sessions:
        del _sessions[sid]
    response.delete_cookie(SESSION_COOKIE, httponly=True)


METHODS = {"GET": "read", "POST": "add", "PUT": "set", "DELETE": "del"}


def protected(page_name):
    """
    Decorator for adding basic authentication protection to a route.

    @param page_name: Name of the page being protected. Some of the parts may be
                      a pattern that has to be replaced with a real part when the
                      query is performed.
    @type  page_name: C{list} of C{str}
    """

    def decorator(func):
        def wrapper(*a, **ka):
            pname = [ka.get(p, p) for p in page_name] + [METHODS.get(request.method, "-")]
            prjname = ka.get("prjname")
            lngname = ka.get("lngname")

            if (
                request.auth
                and translators_password
                and request.auth[0] == "translators"
                and request.auth[1] == translators_password
            ):
                userauth = _script_auth
            else:
                userauth = get_session()

            # We must read all uploaded content before returning a response.
            # Otherwise the connection may be closed by the server and the client aborts.
            for f in request.files:
                pass

            if userauth is None:
                # No authentication backend.
                abort(403, "Access denied")
            elif userauth.may_access(pname, prjname, lngname):
                # Access granted.
                return func(userauth, *a, **ka)
            elif not userauth.is_auth:
                # Not logged in.
                if request.path == "/login":
                    # Help devs out with some very basic protection against a redirect loop
                    raise RuntimeError("No access to /login, rights.dat configuration is missing")
                redirect("/login", redirect=request.path)
            elif prjname is not None and prjname in config.cache.projects:
                # Valid user, but insufficient permissions: Go to project page.
                redirect("/project/<prjname>", prjname=prjname.lower(), message="Access denied")
            else:
                # Valid user, no project context: Go to project list.
                redirect("/projects", message="Access denied")
            return None

        return wrapper

    return decorator
