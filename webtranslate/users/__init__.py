"""
User handling.

Whatever system you make, it needs to deliver the following interface:

- init() Called once to initialize the user system.
- may_access(user, pwd, pname, prjname, lngname) -> boolean May a user access a page?
"""

from webtranslate.users import development, redmine

# Currently there are two user management modules, 'development' and 'redmine'.
# Uncomment the one you want.

module = development
#module = redmine

init = module.init
may_access = module.may_access
