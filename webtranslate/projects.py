"""
Projects and project data.
"""
import os, json

from webtranslate import config, language

PROJECT_CONFIG_NAME = "config.dat"
LANG_EXTENSION = ".lang_dat"

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

        self.languages = {}
        self.load_languages()


    def load_languages(self):
        lang_dir = self.projects.get_projectdir(self.dir_name)
        if lang_dir is None:
            return

        for name in os.listdir(lang_dir):
            if not name.endswith(LANG_EXTENSION):
                continue

            path = os.path.join(lang_dir, name)
            if not os.path.isfile(path):
                continue

            print("Loading language {}".format(path))
            handle = open(path, 'r')
            loaded = json.load(handle)
            handle.close()

            ok = True
            for tag in ('lang-name', 'master-lang', 'last-stamp', 'master-stamp', 'strings'):
                if tag not in loaded:
                    ok = False
                    break
            if ok:
                lang_name = loaded['lang-name']
                master_lang = loaded['master-lang']
                lang = language.Language(path, lang_name, master_lang)
                print("lang_name={!r} master_lang={!r}".format(lang_name, master_lang))

                lang.master_stamp = loaded['master-stamp']
                lang.last_stamp = loaded['last-stamp']
                self.languages[lang_name] = lang


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
