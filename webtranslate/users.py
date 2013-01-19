"""
Users and their access rights.
"""
import json

from webtranslate import config

class Users:
    """
    Data about users and their access rights.

    @ivar users: Users access rights, mapping of user to tuple (pwd, tree of access rights).
    @type users: C{dict} of C{str} to tuple (C{str}, nested dictionaries of access rights).
    """
    def __init__(self):
        self.users = {}

    def load(self):
        self.users = {}
        fname = config.config.get_users_file()
        if fname is None:
            return

        handle = open(fname, 'r')
        loaded = json.load(handle)
        handle.close()
        for entry in loaded:
            self.load_user(entry)

    def load_user(self, entry):
        if 'name' not in entry or 'password' not in entry or 'allow' not in entry:
            return

        name  = entry.get('name')
        pwd   = entry.get('password')
        allow = entry.get('allow')

        if name in self.users:
            return # Don't allow overwriting

        # XXX Check username and password sanity.
        allowed = {}
        self.users[name] = (pwd, allowed)

        if (pwd is None or len(pwd) == 0) and name is not None:
            # A real user must have a non-empty password, or you cannot do anything
            return

        for right in allow:
            # XXX Check sanity of the components
            cs = right.split('/')
            if len(cs) != 4:
                allowed.clear()
                return
            d = allowed
            for c in cs[:3]:
                if c in d:
                    d = d[c]
                else:
                    e = {}
                    d[c] = e
                    d = e

            if cs[3] in d:
                allowed.clear()
                return
            d[cs[3]] = True

    def may_access(self, access, user, password):
        """
        May a user be given access?

        @param access: Requested access (4 elements long).
        @type  access: C{list} of C{str}

        @param user: User requesting the access (may be C{None}).
        @type  user: C{None} or C{str}

        @param password: User requesting the access (may be C{None}).
        @type  password: C{None} or C{str}
        """
        assert len(access) == 4

        n = self.users.get(user)
        if n is None or n[0] != password:
            print("Access: {!r} had a wrong password".format(user))
            return False
        d = n[1]
        for a in access:
            e = d.get(a)
            if e is None:
                e = d.get('*')
            if e is None:
                print("Access: {!r} tried '{}'".format(user, "/".join(access)))
                return False
            d = e
        if d != True:
            print("Access: {!r} tried '{}'".format(user, "/".join(access)))
            return False
        return True


users = Users()


methods = {'GET': 'read', 'POST': 'add', 'PUT': 'set', 'DELETE': 'del'}
general_page_names = set(['root', 'projects'])
project_page_names = set(['single_project'])

def may_access(page_name, path, meth, user, passwd):
    """
    May the given user be given access?

    @param page_name: Page name being accessed.
    @type  page_name: C{str}

    @param path: Path of the page.
    @type  path: C{str}

    @param meth: Type of operation performed at the page.
    @type  meth: C{str}

    @param user: User name.
    @type  user: C{str}

    @param passwd: Password
    @type  passwd: C{str}
    """
    if page_name[0] in general_page_names:
        access = page_name + [methods[meth]]
    elif page_name[0] in project_page_names:
        access = page_name + [methods[meth]]
    else:
        print("Access: Weird access right {!r}".format(page_name))
        return False

    return users.may_access(access, user, passwd)
