"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Called once to initialize the user system.
- may_access(user, pwd, pname, prjname, lngname) -> boolean May a user access a page?
"""
from webtranslate.users import development

init = development.init
may_access = development.may_access
