"""
Projects and project data.
"""
import os, json

from webtranslate import config, language, timestamp

PROJECT_CONFIG_NAME = "config.dat"
LANG_EXTENSION = ".lang_dat"

def load_language_metadata(path, data):
    """
    Load the meta-data of a language.

    @param path: Path to the language file.
    @type  path: C{str}

    @param data: Data to load.
    @type  data: C{dict}

    @return: The loaded language if loading was successful.
    @rtype:  L{Language} or C{None}
    """
    for tag in ('lang-name', 'master-lang', 'last-stamp', 'master-stamp', 'strings'):
        if tag not in data:
            return None

    lang_name = data['lang-name']
    master_lang = data['master-lang']
    lng = language.Language(path, lang_name, master_lang)
    lng.master_stamp = data['master-stamp']
    lng.last_stamp = data['last-stamp']
    return lng


def load_text_string(data):
    """
    Load a text-string.

    @param data: Data to load.
    @type  data: C{dict} with C{"text"} and C{"stamp"}

    @return: The loaded text string if successful.
    @rtype:  C{None} or L{TextString}
    """
    if 'text' not in data or 'stamp' not in data:
        return None

    stamp = timestamp.stamper.read_stamp(data['stamp'])
    if stamp is None:
        print("'stamp' load {} failed".format(data['stamp']))
        return None

    return language.TextString(data['text'], stamp)


def load_master_string(data):
    """
    Load a master string (that is, a non-translated language).

    @param data: String entry to load.
    @type  data: C{dict} with C{"name"} and C{"master"}

    @return The loaded entry, if loading was a success.
    @rtype: C{MasterString} or C{None}
    """
    if 'name' not in data or 'master' not in data:
        return None

    ts = load_text_string(data['master'])
    if ts is None:
        return None

    return language.MasterString(data['name'], ts)


def load_translated_string(data):
    """
    Load a translated string.

    @param data: String entry to load.
    @type  data: C{dict} with C{"name"}, C{"text"}, C{"orig"}, and C{"master"}.

    @return The loaded entry, if loading was a success.
    @rtype: C{TranslatedString} or C{None}
    """
    if 'name' not in data or 'text' not in data or 'orig' not in data or 'master' not in data:
        print("load_translated_string: Insufficient entries")
        return None

    text = data['text']
    if text is not None:
        text = load_text_string(text)
        if text is None:
            print("'text' load of {} failed".format(data['name']))
            return None

    orig = data['orig']
    if orig is not None:
        orig = load_text_string(orig)
        if orig is None:
            print("'orig' load of {} failed".format(data['name']))
            return None

    master = data['master']
    if master is not None:
        master = load_text_string(master)
        if master is None:
            print("'master' load of {} failed".format(data['name']))
            return None

    return language.TranslatedString(data['name'], text, orig, master)


class ProjectData:
    """
    Data of a project.

    @ivar dir_name: Name of the project (directory name at the disk).
    @type dir_name: C{str}

    @ivar projects: Overall projects manager.
    @type projects: L{Projects}

    @ivar description: Description of the project.
    @type description: C{str}

    @ivar website: Web site of the project.
    @type website: C{str} or C{None} if not available.

    @ivar languages: Languages of the project.
    @type languages: C{dict} of L{Language}

    @ivar lang_system: Language system of the project.
    @type lang_system: L{LanguageSystem}
    """
    def __init__(self, dir_name, projects):
        self.dir_name = dir_name
        self.projects = projects
        self.lang_system = None
        self.clear()

    def clear(self):
        """
        Reset most data values.
        """
        self.description = ""
        self.website = None
        self.languages = {}

    def load(self):
        """
        Load data of a project.
        """
        cfg_name = self.projects.get_projectdir(self.dir_name)
        if cfg_name is None:
            return
        cfg_name = os.path.join(cfg_name, PROJECT_CONFIG_NAME)
        if not os.path.isfile(cfg_name):
            return

        handle = open(cfg_name, 'r')
        loaded = json.load(handle)
        handle.close()

        if 'description' not in loaded:
            self.clear()
            return
        self.description = loaded['description']

        self.website = None
        if 'website' in loaded:
            self.website = loaded['website']

        # self.lang_system is not cleared to increase the chance of having a sane value.
        if 'language-system' in loaded:
            ls = loaded['language-system']
            ls = language.language_systems.get(ls)
            if ls is not None:
                self.lang_system = ls()

        # Load meta-data of the languages.
        self.languages = {}
        lang_dir = self.projects.get_projectdir(self.dir_name)
        if lang_dir is None:
            return

        for name in os.listdir(lang_dir):
            if not name.endswith(LANG_EXTENSION):
                continue

            path = os.path.join(lang_dir, name)
            if not os.path.isfile(path):
                continue

            #print("Loading language {}".format(path))
            handle = open(path, 'r')
            loaded = json.load(handle)
            handle.close()

            lng = load_language_metadata(path, loaded)
            if lng is not None:
                self.languages[lng.lang_name] = lng

        # XXX Verify master_lang setting of all languages.

    def load_strings(self, lname):
        """
        Load the strings of a language in the project. If the loaded language
        has a master language, ensure the latter is available too, and
        synchronize both.

        @param lname: Name of the language to load.
        @type  lname: C{str}
        """
        lng = self.languages.get(lname)
        if lng is None:
            return None # Don't load non-existing languages
        if lng.strings is None:
            self._load_strings(lng)

        if lng.master_lang is None:
            return lng

        mlng = self.languages.get(lng.master_lang)
        if mlng is None:
            print("Missing master language of '{}'".format(lng.lang_name))
            return None

        if mlng.strings is None:
            self._load_strings(mlng)

        self.sync_language(lng, mlng)
        return lng


    def _load_strings(self, lng):
        """
        Load the strings of a language in the project.

        @param lng: Language to load.
        @type  lng: L{Language}
        """
        assert lng is not None and lng.strings is None

        handle = open(lng.lang_file, 'r')
        loaded = json.load(handle)
        handle.close()

        texts = {}
        if 'strings' not in loaded:
            return

        for str_loaded in loaded['strings']:
            if lng.master_lang is None:
                entry = load_master_string(str_loaded)
            else:
                entry = load_translated_string(str_loaded)

            if entry is None or entry.name in texts:
                return

            texts[entry.name] = entry

        lng.strings = language.Strings(texts)
        # XXX Check/update last_stamp

    def sync_language(self, tlng, mlng):
        """
        Synchronize a translated language with its master language.

        @param tlng: Translated language.
        @type  tlng: L{Language}

        @param mlng: Master language of the translation.
        @type  mlng: L{Language}
        """
        assert tlng is not None and mlng is not None

        ttexts = tlng.strings.texts
        mtexts = mlng.strings.texts
        modified = False

        # Delete and update strings that are not in the master language any more.
        to_delete = []
        for tname, tstr in ttexts.items():
            if tname not in mtexts:
                # Remove old string.
                to_delete.append(tname)
                modified = True
            else:
                # Update translation if necessary.
                mstr = mtexts[tname]
                if tstr.orig is not None:
                    if mstr.master.text == tstr.orig.text:
                        continue # Translated 'orig' text is the same as the master text.
                if tstr.master is not None and tstr.master.text == mstr.master.text:
                    continue # Translated 'master' text is the same as the master text.
                # Set a new 'master' string in the translation.
                tstr.master = mstr.master
                modified = True
                # XXX Update last_stamp

        for tname in to_delete: # Actually delete the old strings.
            del ttexts[tname]

        # Add new master strings
        # XXX Update last_stamp
        for mname, mval in mtexts.items():
            if mname not in ttexts:
                # New string
                ttexts[mname] = language.TranslatedString(mname, None, None, mval)
                modified = True

        # XXX Handle 'modified'


class Projects:
    """
    Projects of the web translator.

    @ivar projects: Available projects, mapping of name to its information.
    @type projects: C{dict} of C{str} to L{ProjectData}

    @ivar proj_root: Root directory of the projects.
    @type proj_root: C{str}, or C{None} if not retrieved from the config yet.
    """
    def __init__(self):
        self.projects = {}
        self.proj_root = None

    def get_projectdir(self, proj_name = None):
        """
        Get the directory containing the project with the given name, or the
        project root directory.

        @param proj_name: Name of the project, if provided.
        @type  proj_name: C{str}, or C{None} for the project root directory.

        @return: Path the requested directory, or C{None} if it is not available.
        """
        if self.proj_root is None:
            self.proj_root = config.config.get_projects_dir()
            if self.proj_root is None:
                return None

        if proj_name is None:
            return self.proj_root
        else:
            dirname = os.path.join(self.proj_root, proj_name)
            if not os.path.isdir(dirname):
                return None
            return dirname


    def load(self):
        """
        Load the available projects.
        """
        self.projects = {}

        proj_dir = self.get_projectdir()
        if proj_dir is None:
            return
        for name in os.listdir(proj_dir):
            # Check that
            config_path = os.path.join(proj_dir, name, PROJECT_CONFIG_NAME)
            if not os.path.isfile(config_path):
                continue

            pd = ProjectData(name, self)
            pd.load()
            self.projects[name] = pd

projects = Projects()
