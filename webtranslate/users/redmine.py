"""
User and webpage management handled by RedMine (http://www.redmine.org/).

The owner and translators of the rights are mapped to roles in RedMine through
the C{<redmine/>} section in the config file.

A lot of the magic in this file has been copied from hgweb.py in https://bitbucket.org/nolith/hgredmine/


This code is not thread-safe!!
"""
import hashlib
from webtranslate import rights

# Also initialized in the config loader.
db_type = None
db_schema = None
db_name = None
db_password = None
db_user = None
db_host = None
db_port = None

owner_role = None
translator_roles = {} # Mapping of iso language name to role name.

db_connection = None

def init():
    """
    Initialize the user admin system.
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection

    db_connection = None

    if db_name is None or db_name == "": return

    # Setup connection.
    if db_type == 'postgress':
        import psycopg2, psycopg2.extras, psycopg2.extensions
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

        dsn = "dbname='{}' user='{}' host='{}' password='{}' port={}".format(db_name, db_user, db_host, db_password, db_port)
        db_connection = psycopg2.connect(dsn)
        db_connection.set_client_encoding('UTF-8')

        if db_schema is not None and db_schema != "":
            try:
                cur = db_connection.cursor()
                cur.execute("SET search_path TO %s", (db_schema,))
                db_connection.commit()
            except KeyError:
                pass


    elif db_type == 'mysql':
        import MySQLdb

        db_connection = MySQLdb.connect(user=db_user, passwd=db_password, host=db_host, port=db_port, db=db_name, use_unicode=True)

    elif db_type == 'sqlite3':
        import sqlite3

        db_connection = sqlite3.connect(db_name)
    else:
        db_connection = None # There is no db connection.


def may_access(user, pwd, pname, prjname, lngname):
    """
    May a user access a page?

    @param user: Name of the user, if provided (external data).
    @type  user: C{str} or C{None}

    @param pwd: Password of the user, if provided (external data).
    @type  pwd: C{str} or C{None}

    @param pname: Page name being accessed.
    @type  pname: C{list} of C{str}

    @param prjname: Project name of the page, if any.
    @type  prjname: C{str} or C{None}

    @param lngname: Language name of the page, if any.
    @type  lngname: C{str} or C{None}

    @return: Whether the user may access the page.
    @rtype:  C{bool}
    """
    global db_type, db_schema, db_name, db_password, db_user, db_host, db_port, db_connection
    global owner_role, translator_roles

    if db_connection is None: return False  # No connection -> Always refuse.

    # Verify user.
    # Note that failure to authenticate is not fatal, it falls back to an 'unknown' user.
    if user is not None and user != "" and pwd is not None:
        if db_type == 'postgress' or db_type == 'mysql':
            cur = db_connection.cursor()
            cur.execute("SELECT users.hashed_password, users.salt FROM users WHERE users.login=%s", (user,))
            row = cur.fetchone()

        elif db_type == 'sqlite3':
            cur = db_connection.cursor()
            cur.execute("SELECT users.hashed_password, users.salt FROM users WHERE users.login=?", (user,))
            row = cur.fetchone()
        else:
            return False

        if not row:
            user = None
        else:
            hashed_password = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
            result_hash = row[0]
            result_salt = row[1]
            salted_hash = hashlib.sha1((result_salt + hashed_password).encode('ascii')).hexdigest()
            if salted_hash != result_hash:
                user = None

    # Get page access rights for all types of users.
    if user is None or user == "":
        user = "unknown"

    accesses = rights.get_accesses(pname, user)
    if accesses[user] == True or accesses['SOMEONE'] == True: return True

    # User must get access through a OWNER or TRANSLATOR role.
    if prjname is None or user == "unknown": return False

    if db_type == 'postgress' or db_type == 'mysql':
        cur = db_connection.cursor()
        cur.execute("""SELECT roles.name FROM users, members, projects, member_roles, roles
                       WHERE users.login=%s
                         AND users.id = members.user_id
                         AND projects.identifier=%s
                         AND projects.id = members.project_id
                         AND members.id = member_roles.member_id
                         AND member_roles.role_id = roles.id""", (user, prjname))
        rows = cur.fetchall()

    elif db_type == 'sqlite3':
        cur = db_connection.cursor()
        cur.execute("""SELECT roles.name FROM users, members, projects, member_roles, roles
                       WHERE users.login=?
                         AND users.id = members.user_id
                         AND projects.identifier=?
                         AND projects.id = members.project_id
                         AND members.id = member_roles.member_id
                         AND member_roles.role_id = roles.id""", (user, prjname))
        rows = cur.fetchall()
    else:
        return False

    roles = set(r[0] for r in rows)
    if lngname is not None and accesses['TRANSLATOR'] == True:
        rm_role = translator_roles.get(lngname)
        if rm_role is not None and rm_role != "" and rm_role in roles: return True

    if accesses['OWNER'] == True:  # 'prjname is not None' has been already established.
        if owner_role is not None and owner_role != "" and owner_role in roles: return True

    return False

