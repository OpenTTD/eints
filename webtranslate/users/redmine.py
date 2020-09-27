"""
User and webpage management handled by RedMine (http://www.redmine.org/).

The owner and translators of the rights are mapped to roles in RedMine through
the C{<redmine/>} section in the config file.

A lot of the magic in this file has been copied from hgweb.py in https://bitbucket.org/nolith/hgredmine/


This code is not thread-safe!!
"""
import hashlib
import logging
import time

from .. import (
    rights,
    userauth,
)

log = logging.getLogger(__name__)

# Also initialized in the config loader.
db_type = None
db_schema = None
db_name = None
db_password = None
db_user = None
db_host = None
db_port = None

owner_role = None
translator_roles = {}  # Mapping of iso language name to role name.

db_connection = None


class RedmineUserAuthentication(userauth.UserAuthentication):
    """
    Implementation of UserAuthentication for Redmine authentication system.
    """

    def __init__(self, is_auth, name, project_roles):
        super(RedmineUserAuthentication, self).__init__(is_auth, name)
        self.project_roles = project_roles

    def get_roles(self, prjname, lngname):
        eints_roles = set()
        if self.is_auth:
            eints_roles.add("USER")

            rm_roles = None
            if prjname is not None:
                rm_roles = self.project_roles.get(prjname)

            if rm_roles is not None:
                if owner_role is not None and owner_role != "" and owner_role in rm_roles:
                    eints_roles.add("OWNER")

                lang_role = None
                if lngname is not None:
                    lang_role = translator_roles.get(lngname)

                if lang_role is not None and lang_role != "" and lang_role in rm_roles:
                    eints_roles.add("TRANSLATOR")

        return eints_roles


def connect():
    """
    Try to connect to the data base.

    @return: Whether we are connected (not 100% certain).
    @rtype:  C{bool}
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection

    if db_connection is not None:
        return True  # Already connected.

    if db_name is None or db_name == "":
        return

    # Setup connection.
    if db_type == "postgress":
        import psycopg2
        import psycopg2.extras
        import psycopg2.extensions

        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

        dsn = "dbname='{}' user='{}' host='{}' password='{}' port={}".format(
            db_name, db_user, db_host, db_password, db_port
        )
        # In case the db is down, we probably get an error here.
        # try:
        db_connection = psycopg2.connect(dsn)
        # except psycopg2.XXXXError: # Don't know what to catch :(
        #   db_connection = None
        #   return False

        db_connection.set_client_encoding("UTF-8")

        if db_schema is not None and db_schema != "":
            try:
                cur = db_connection.cursor()
                cur.execute("SET search_path TO %s", (db_schema,))
                db_connection.commit()
            except KeyError:
                pass

        return True

    elif db_type == "mysql":
        import MySQLdb

        db_connection = MySQLdb.connect(
            user=db_user, passwd=db_password, host=db_host, port=db_port, db=db_name, use_unicode=True
        )
        return True

    elif db_type == "sqlite3":
        import sqlite3

        db_connection = sqlite3.connect(db_name)
        return True

    else:
        db_connection = None
        return False


def _do_command(cmd, parms):
    """
    Internal function to perform a command. Use L{query} instead.

    @param cmd: Command to perform.
    @type  cmd: C{str}

    @param parms: Parameters of the command.
    @type  parms: C{tuple} of C{str}

    @return: Cursor with the result, if all went well, else C{None}
    @rtype:  db cursor, or C{None}
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection

    if db_type == "postgress":
        import psycopg2

        cur = db_connection.cursor()
        try:
            cur.execute(cmd, parms)
            return cur
        except psycopg2.OperationalError:
            # Administrator closed the connection.
            db_connection = None
            return None

    else:
        # For other data bases, assume good weather behavior until proven otherwise.
        cur = db_connection.cursor()
        cur.execute(cmd, parms)
        return cur


def query(cmd, parms):
    """
    Perform a query with the data base.

    @param cmd: Command to perform.
    @type  cmd: C{str}

    @param parms: Parameters of the command.
    @type  parms: C{tuple} of C{str}

    @return: Cursor with the result, if all went well, else C{None}
    @rtype:  db cursor, or C{None}
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection

    count = 0
    while count < 3:
        # Connect if not connected.
        if db_connection is None:
            if not connect():
                log.error("Eints: Failed to connect to the data base.")
                time.sleep(10)  # Avoid flooding.
                return None

            assert db_connection is not None

        cur = _do_command(cmd, parms)
        if cur is not None:
            return cur

        log.warning("Attempt %d, query failed.", count)
        time.sleep(10)
        count = count + 1

    return None  # 3 Failures, not going to work.


def init():
    """
    Initialize the user admin system.
    """
    global db_connection

    rights.init_page_access()

    db_connection = None
    connect()  # Not really needed, but perhaps useful?


def get_authentication(user, pwd):
    """
    Authenticate a user and return an authentication object.

    @param user: Name of the user, if provided (external data).
    @type  user: C{str} or C{None}

    @param pwd: Password of the user, if provided (external data).
    @type  pwd: C{str} or C{None}

    @return: UserAuthentication object to test accesses with.
    @rtype: C{UserAuthentication}
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection
    global owner_role, translator_roles

    # Verify user.
    # Note that failure to authenticate is not fatal, it falls back to an 'unknown' user.
    if user is not None and user != "" and pwd is not None:
        if db_type == "postgress" or db_type == "mysql":
            cur = query("SELECT users.hashed_password, users.salt FROM users WHERE users.login=%s", (user,))
            if cur is None:
                return RedmineUserAuthentication(False, "unknown", dict())

            row = cur.fetchone()

        elif db_type == "sqlite3":
            cur = query("SELECT users.hashed_password, users.salt FROM users WHERE users.login=?", (user,))
            if cur is None:
                return RedmineUserAuthentication(False, "unknown", dict())

            row = cur.fetchone()
        else:
            return None

        if not row:
            user = None
        else:
            hashed_password = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
            result_hash = row[0]
            result_salt = row[1]
            salted_hash = hashlib.sha1((result_salt + hashed_password).encode("ascii")).hexdigest()
            if salted_hash != result_hash:
                user = None
    else:
        user = None

    if user is None:
        return RedmineUserAuthentication(False, "unknown", dict())

    # Fetch roles from database
    cur = query(
        """SELECT projects.identifier, roles.name FROM users, members, projects, member_roles, roles
                   WHERE users.login=%s
                     AND users.id = members.user_id
                     AND projects.id = members.project_id
                     AND members.id = member_roles.member_id
                     AND member_roles.role_id = roles.id""",
        (user,),
    )
    if cur is None:
        return RedmineUserAuthentication(False, "unknown", dict())

    rows = cur.fetchall()

    roles = dict()
    for r in rows:
        prj = roles.setdefault(r[0], set())
        prj.add(r[1])

    return RedmineUserAuthentication(True, user, roles)
