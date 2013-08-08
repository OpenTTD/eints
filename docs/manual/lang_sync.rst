Batch operations
================

Eints is entirely built as web service, which is great for interactively
handling translated strings. However, sometimes it is useful to do the same
operations in batch from the command line or from a script.

For this purpose, the ``lang_sync`` program exists. Like the Eints service, it
is written in `Python 3 <http://www.python.org/>`_. It can

- Create a project in Eints.
- Upload the base language and the translations.
- Download the base language and the translations.

It operates by programmatically accessing the Eints service.


Options
-------
For its operations, ``lang_sync`` needs a lot of information, which is
provided through option values. While technically you can run the program
manually from the command line, but the number of option values is so large
that wrapping the execution in a script is useful.

General options
~~~~~~~~~~~~~~~
The general options are

.. option:: -h, --help

   Get the online help text.

.. option:: --verbose

   Show what the program is doing

.. option:: --no-write

   Don't make actual changes to any file

Eints access
~~~~~~~~~~~~

Getting access to the Eints web application is useful to get anything done.
Basically it needs to get the user name and password, which can be given in a
number of different ways

.. option:: --user-password-file = FILE

   If given, FILE contains lines of the form::

       username: <username>
       password: <password>

   with ``<username>`` the actual user name, and ``<password>`` the actual
   password. If needed, quotes may be used around the user name or password.

.. option:: --user = <username>

   If the file was not provided, or did not contain a user name, specifying
   the user name at the command-line is a second solution.
   At multi-user systems, this is however not secure, everybody can query the
   application parameters while the program is running.

.. option:: --password = <password>

   If no file is given, or it did not contain a password, specifying the
   password at the command line is another (but not so good) solution.

   At a multi-user system this is not secure, and should be avoided.

.. option:: --not-interactive

   The last option to get the user name and password is using the standard
   Python
   `getpass <http://docs.python.org/3/library/getpass.html#module-getpass>`_ module.
   This will ask for the password at the command-line.
   This option prevents use of this module, so ``lang_sync`` will not
   become stuck at waiting for user input.

.. option:: --base-url = <baseurl>

   The scheme and host part of the Eints service URL. Typically a string
   like::

    https://eints.example.com/


Project information
~~~~~~~~~~~~~~~~~~~

The other important part is the project that is accessed. Depending on the
performed operations, some options may be omitted. Adding options that are not
used is however allowed.

.. option:: --project = <project-identifier>

   Name of the project in Eints (may contain letters, digits, and dashes).

.. option:: --project-desc = <project-description>

   For project creation, a longer title of the project (may contain letters,
   digits, dashes and spaces).

.. option:: --project-url = <website-url>

   For project creation, an optional website URL.

.. option:: --lang-dir = <lang-dir>

   For uploading or downloading language files, the path of the directory
   containing the language files at the local disc.
   (Default: ``lang``.)

.. option:: --lang-file-ext = <lang-ext>

   For uploading or downloading language files, the filename suffix used by
   the language files. (Default: ``.lng``.)

.. option:: --base-language = <grf-langid>

   For uploading or downloading language files, in case Eints does not know
   the base language (mostly at initial import),
   this option can be used to specify it manually. It must be the same number
   as given at a ``##grflangid`` line (a string of the form ``0x[HEX][HEX]``.)

.. option:: --language-file-mapping = <filename>

   When downloading new languages, the program creates new language files. It
   has a list of well-known language base filenames, but for unknown
   languages or when the default base filename is not good, this option can be
   used to override the default.

   Lines of the files should have the form::

    0x[HEX][HEX]: <base-filename>

   Line comments start with a ``#``, and empty lines are silently ignored.

Operations
~~~~~~~~~~

The actual operations that should be performed by the script are given as
command-line arguments after the options.
Currently, five operations are supported:

``download-base``
    Download the base language file from Eints.

``download-translations``
    Download all the translations from Eints.

``upload-base``
    Upload the base language file to Eints.

``upload-translations``
    Upload all the translation files to Eints.

``create-project``
    Create a new project in Eints.

You can add several operations at the command line, they are executed
sequentially.

There are a few restrictions to consider. You cannot upload or download before
having created the project, and upload after download is useless, since the
download will overwrite the local language files.


.. vim: sw=4 sts=4 tw=78 spell
