"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Call to initialize the user system.
- authenticate(user, passwd) -> boolean  Is the user/password combination correct?
"""
from webtranslate.users import silly

init = silly.init
authenticate = silly.authenticate
