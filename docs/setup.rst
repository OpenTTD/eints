Author: alberth and andythenorth
Date:   March 2013

======================
Installation and setup
======================
Eints is written in Python 3. In its default setup (which is not intended for
production use), nothing else is needed.

Internally, it uses:

- `Bottle <http://bottlepy.org/>`_, a Python framework for writing web applications.
    - Location: webtranslate/bottle.py
    - Licensed under `MIT License <http://bottlepy.org/docs/dev/#license>`_
- `Twitter Boostrap <http://twitter.github.com/bootstrap/>`_, a CSS, JS and glyphicon framework for web application user interfaces.
    - Locations: static/css static/img static/js
    - Code licensed under `Apache License v2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_,
    - Documentation licensed under `CC BY 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
    - Glyphicons Free licensed under `CC BY 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
- `WooCons #1 <http://www.woothemes.com/2010/08/woocons1/>`_, an icon library.
    - Location: static/img/woocons1
    - Licensed under `GPL v3 <http://www.gnu.org/licenses/gpl.html>`_

Setup
=====
After unpacking, Eints needs to be configured.

Global configuration
--------------------
The global configuration settings are in ``config.xml``. It has the following
entries:

project-root
  Root directory of the data files for each project, including the backup
  files.

project-cache
  Eints loads project data files when needed. To reduce memory requirements,
  this setting controls how many data files it may keep in memory.

language-file-size
  Eints can download NML language files. This setting control the maximum size
  of such files.

num-backup-files
  When the data of a project is changed, Eints writes a new copy of the
  project data to disk. This setting controls how many previous versions are
  kept.

max-num-changes
  Eints enables changing of strings in translations. For reference purposes, a
  number of previous texts for each string (in each language in each project)
  are kept. This setting controls how many can exist at most.

min-num-changes
  Controls the minimum number of texts to keep for each string. Should be at
  least ``1``.

change-stable-age
  When a string is being changed, the change is 'unstable', and will be kept
  for a while. This setting controls when such a change is sufficiently old to
  consider again for deletion (if the change count is above
  ``min-num-changes``).


Access rights
-------------
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
- A literal username,
- The ``*`` wildcard, matching everybody,
- ``SOMEONE``, matching unauthenticated users,
- ``OWNER``, a user denoted as owner of the project that is accessed through
  the path.
- ``TRANSLATOR``, a user that is registered as translator for a language in a
  project, for paths that deal with languages. Obviously being an ``OWNER``
  implies being an ``TRANSLATOR`` for all languages in the project.

Paths look a lot like the paths used by Eints for the URI of the web-pages. A
path however always has four elements, namely *action*, *project*, *language*,
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

        # Root is accessible by all
        * + /root/-/-/*

        # Unauthenticated users don't get any further
        SOMEONE - /*/*/*/*

        # 'admin' user can do anything
        admin + /*/*/*/*

        # Authenticated users can see the projects, see each project, download a
        # language, and get an overview of a language in a project.
        * + /projects/-/-/read
        * + /project/*/-/read
        * + /download/*/*/read
        * + /language/*/*/read

        # Strings editing
        OWNER      + /string/*/*/*
        TRANSLATOR + /string/*/*/*

        # Language file uploading, and language deletion
        OWNER + /upload/*/-/*
        OWNER + /delete/*/*/*

Note that by default, Eints defines no users at all. ``admin`` will thus not
work without creating such a user first.

Project owners and translators
------------------------------
In the above section, user categories ``OWNER`` and ``TRANSLATOR`` may be used to
define who can access certain pages.
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


Users
-----
Users send authentication information using standard HTTP basic authentication
to the web server. As such, it is highly recommended to use the ``https``
protocol for the translator service.

At the server, the sent information has to be compared with locally available
user data base. How to do that should be defined in
``webtranslate/users/__init__.py``. By default a simple user system called
``silly`` is provided, **aimed at testing only**.
It *stores users and their passwords in plain text* (in ``users.dat``). The
``editsilly`` program can add, update, and remove users from the file.

Currently, Eints does not provide interfaces to other user administration
systems. They will have to be programmed in the above mentioned Python file.

.. vim: tw=78 spell
