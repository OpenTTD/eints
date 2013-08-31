
.. contents::

======================
Installation and setup
======================
Eints is written in `Python 3 <http://www.python.org/>`_. Its software uses the `GPL V2
<http://www.gnu.org/licenses/gpl-2.0.html>`_. For stand-alone use (which is
useful for development and testing), no other software is needed.

Internally, it uses:

- `Bottle <http://bottlepy.org/>`_, a Python framework for writing web applications.
  - Location: webtranslate/bottle.py
  - Licensed under `MIT License <http://bottlepy.org/docs/dev/#license>`_
- `Twitter Boostrap <http://twitter.github.com/bootstrap/>`_, a CSS, JS and glyphicon framework
  for web application user interfaces.
  - Locations: static/css static/img static/js
  - Code licensed under `Apache License v2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_,
  - Documentation licensed under `CC BY 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
  - Glyphicons Free licensed under `CC BY 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
- `WooCons #1 <http://www.woothemes.com/2010/08/woocons1/>`_, an icon library.
  - Location: static/img/woocons1
  - Licensed under `GPL v3 <http://www.gnu.org/licenses/gpl.html>`_

The Eints repository includes files of the above projects for your
convenience. They are however not part of Eints.

Setup
=====
After downloading and unpacking, Eints needs to be configured:

- A :ref:`server_configuration` must be set up.
- :ref:`page_access_rights` must be set up.

If the authentication in the ``config.xml`` file is set to ``development``,
additional configuration file must be set up:

- :ref:`project_owners_translators` must be set up.
- :ref:`users_passwords` must be set up.

If the authentication in the ``config.xml`` file is set to ``redmine``, the
latter information is retrieved from the Redmine data base, as explained in
:ref:`redmine_configuration_setup`.


.. _server_configuration:

Server configuration
--------------------
The global configuration settings are in ``config.xml``. It has the following
entries:

Note that Eints is not thread-safe, trying to use it with multiple threads
will fail to work properly.

Server setup
~~~~~~~~~~~~
The following configuration fields exist for the general server set up.

*server-mode*
    Mode of the server, must be either ``development``, ``production`` or
    ``mod_wsgi``. The former two will start a bottle web server. In
    *development* mode, errors that happen in the server process are copied into
    the generated html page. The latter allows deployment via apache's mod_wsgi.
    See :ref:`apache_mod_wsgi` for an example configuration with mod_wsgi.

*server-host*
    Name of the host that should provides the Eints service.

*server-port*
    Port number of the host that should provide the Eints service.

*authentication*
    Method of authentication. Currently supported forms are:

    * ``development`` which uses local files for everything, or
    * ``redmine`` which hooks into the `Redmine <http:www.redmine.org>`_ software for
      roles and users.

Eints uses basic authentication to authenticate users. For this reason, the
Eints service should be remotely accessible only through a secure connection.


.. XXX links and references

.. _apache_mod_wsgi:

Server setup with apache's mod_wsgi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Below is an example apache2 configuration assuming eints to reside
in the directory ``/home/eints/eints``::

    WSGIPythonPath /home/eints/eints
    <VirtualHost *:80>
        ServerAdmin webmaster@localhost

        WSGIDaemonProcess eints user=eints group=eints processes=1 threads=1 home=/home/eints/eints
        WSGIScriptAlias / /home/eints/eints/app.wsgi
        WSGIPassAuthorization On

        DocumentRoot /var/www

        <Directory /var/www/>
            WSGIProcessGroup eints
            WSGIApplicationGroup %{GLOBAL}
            Order allow,deny
            allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel warn

        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>


Project data setup
~~~~~~~~~~~~~~~~~~
The following configuration fields exist to define how project data is
treated.

*project-root*
  Root directory of the data files for each project, including the backup
  files.

*project-cache*
  Eints loads project data files when needed. To reduce memory requirements,
  this setting controls how many data files it may keep in memory.

*language-file-size*
  Eints can download `NML <http://dev.openttdcoop.org/projects/nml>` language files.
  This setting control the maximum size in bytes of such files.

*num-backup-files*
  When the data of a project is changed, Eints writes a new copy of the
  project data to disk. This setting controls how many previous versions are
  kept.

*max-num-changes*
  Eints enables changing of strings in translations. For reference purposes, a
  number of previous texts for each string (in each language in each project)
  are kept. This setting controls how many can exist at most. Keep in mind
  that the last uploaded string is always kept to allow comparing with the
  next upload.

*min-num-changes*
  Controls the minimum number of texts to keep for each string. Should be at
  least ``2``. (One for the last uploaded text, and one for the newest
  translation.)

*change-stable-age*
  When a string is being changed, the change is considered 'unstable', and will be kept
  for a while. This setting controls when such a change is sufficiently old to
  consider it 'stable', so it may get deleted if the string count is above
  ``min-num-changes``.

When uploading language files from NML, Eints uses the available strings to
detect whether changes occurred in the file. The ``min-num-changes`` and
``change-stable-age`` values should be chosen such that previously uploaded
information is still available when downloading updates.

.. _redmine_configuration_setup:

Redmine configuration setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~
If Eints *authentication* is using ``redmine``, the redmine part of the
configuration should also be filled in.

*db-type*
    Type of data base used by Redmine.

*db-schema*
    Postgress sometimes needs a search path to find its schema.

*db-user*
    Accoutn which gives read access to the Redmine data base.

*db-password*
    Password of the ``db-user`` entry to get read access to the Redmine data
    base.

*db-host*
    Name of the host to contact for accessing the data base.

*db-port*
    Port number of the ``db-host`` to contact.

Redmine roles setup
~~~~~~~~~~~~~~~~~~~

Eints uses a project owner and translator roles to provide access to its web
pages. These roles are mapped to Redmine roles, so you can setup access control
from the Redmine interface.

*owner-role*
    Name of the Redmine role to denote the user(s) which are considered
    'project owner' for an Eints project.

*translator-role*
    Name of the Redmine role to denote the user(s) which are considered to be
    a translator for one language.

    A translator role must be defined for each language that is used in Eints.
    Each Eints role may map to the same Redmine role however.

    Note that project owner access is implied by translator access by Eints.
    Any page accessible to a translator is also accessible by the owner of the
    project.

.. _page_access_rights:

Page access rights
------------------
The ``rights.dat`` file defines who can access the data. It inspects paths of
web pages being accessed, and checks whether the user performing the operation
should be allowed to proceed.

The file is a list of access rules, that associates users and paths with the
right to access. The general form of a rule is::

        <user> +/- <path>

The ``+/-`` at the first access rule that matches with the user and the path
decides access. The ``+`` means to give access, ``-`` means deny access.
For readability, the file can also have empty lines, and comment lines (a line
starting with ``#`` in the first column).

A ``<user>`` can be

- A literal username (not recommended),
- The ``*`` wildcard, matching everybody,
- ``SOMEONE``, matching unauthenticated users,
- ``OWNER``, a user denoted as owner of the project that is accessed through
  the path.
- ``TRANSLATOR``, a user that is registered as translator for a language in a
  project, for paths that deal with languages. Obviously being an ``OWNER``
  implies being an ``TRANSLATOR`` for all languages in the project.

A <path> looks a lot like the paths used by Eints for the URI of the web-pages. A
path in this file however always has four elements, namely *action*, *project*, *language*,
and *operation*. Each of the elements is a name, the value ``*`` (to denote
its value is not relevant in matching), or the value ``-`` (to denote the
value does not exist).

The *action* is the same as the first component in the URI, except that the
root page uses ``root`` as action. The following actions exist:

- ``root``, the root page,
- ``projects``, the overview page containing all projects,
- ``project``, the overview page of a single project,
- ``language``, the overview page of a language in a project,
- ``string``, the edit page of a single string in a single translation
  language,
- ``upload``, the page to upload language files into Eints,
- ``download``, the download page for getting new language files from Eints,
  and
- ``delete``, the page to delete a language.

The *project* and *language* elements are the name of the project and name of
the language respectively. Usually these are not interesting, access control
is handled with ``OWNER`` and ``TRANSLATOR`` users.

The *operation* element is either ``read`` or ``add``.

For reference purposes, below is an example access rights file::

    # Root, project overview, and download pages are readable by all
    * + /root/-/-/read

    # Unauthenticated users don't get any further
    SOMEONE - /*/*/*/*

    # First pages of project creation can be used by anyone (these pages have no
    # project to authenticate against).
    * + /newproject/-/-/read
    * + /createproject/-/-/add

    # Only the owner can create a project.
    OWNER + /makeproject/*/-/add

    # Authenticated users (of a project) can see the projects, see each project, download a
    # language, and get an overview of a language in a project.
    * + /projects/-/-/read
    * + /project/*/-/read
    * + /download-list/*/*/read
    * + /download/*/*/read
    * + /language/*/*/read

    # Strings editing
    OWNER      + /string/*/*/*
    TRANSLATOR + /string/*/*/*

    # Language file uploading, language deletion and creation
    OWNER + /upload/*/-/*
    OWNER + /delete/*/*/*
    OWNER + /newlanguage/*/-/*
    OWNER + /projsettings/*/-/*

.. _project_owners_translators:

Project owners and translators
------------------------------
In the above section, user categories ``OWNER`` and ``TRANSLATOR`` may be used to
define who can access certain pages.

If the ``authentication`` entry in ``config.xml`` is set to *redmine*, the
Redmine data base is queried for membership of the roles. If the
``authentication`` entry is set to *development*, a local file is used,
explained below.

Membership of a user in these categories is decided in the ``projects.dat``
file. It is a INI file, where the section name is the name of the project, the
keys of a section are the languages, and the values are the names of the users
separated by spaces or commas.
The special 'language' ``owner`` is used to denote project ownership.
An example::

        [eints]
        owner = alberth, andythenorth
        nl_NL = alberth

Here, the ``eints`` project is defined (always lowercase), with two owners,
and one translator for the Dutch language.
(Note that since an owner also has translator access, the final line is not
needed in this example.)


.. _users_passwords:

Users
-----
Users send authentication information using standard HTTP basic authentication
to the web server. As such, it is highly recommended to use the ``https``
protocol for the translator service.

If the ``authentication`` entry in ``config.xml`` is set to *redmine*, the
Redmine data base is queried for user authentication. If the
``authentication`` entry is set to *development*, a local file is used. In the
latter case users and their passwords are stored in plain text in
``users.dat``. Obviously, this is not secure in any way. It should never be
used to store important authentication information. The ``editsilly`` program
can add, update, and remove users from the file, for example

::

        ./editsilly admin

would create or change the ``admin`` account.


.. vim: sw=4 sts=4 tw=78 spell
