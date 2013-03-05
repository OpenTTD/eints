"""
Bottle authentication decorator.
"""
from webtranslate.bottle import request, abort, error, response
#from webtranslate import users

@error(401)
def handle401(error):
    response.set_header('WWW-Authenticate', 'Basic realm="Web translator"')
    return 'Access denied'

def protected(page_name):
    ''' Decorator for adding basic authentication protection to a route. '''
    def decorator(func):
        def wrapper(*a, **ka):
#            if request.auth is None:
#                user, password = None, None
#            else:
#                user, password = request.auth
#            pname = [ka.get(p, p) for p in page_name]
#            if not users.may_access(pname, request.path, request.method, user, password):
#                abort(401, "Access denied")
            user = 'unknown'
            return func(user, *a, **ka)
        return wrapper
    return decorator
