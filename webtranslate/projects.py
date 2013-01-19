"""
Projects and project data.
"""
import os, json

from webtranslate import config

PROJECT_CONFIG_NAME = "config.dat"

class ProjectData:
    """
    Data of a project.

    @ivar dir_name: Name of the project (directory name at the disk).
    @type dir_name: C{str}

    @ivar description: Description of the project.
    @type description: C{str}

    @ivar website: Web site of the project.
    @type website: C{str} or C{None} if not available.

    @ivar languages: Languages of the project.
    @type languages: C{dict} of L{Language}

    @ivar lang_system: Language system of the project.
    @type lang_system: L{LanguageSystem}
    """
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.clear()

    def clear(self):
        """
        Reset most data values.
        """
        self.description = ""
        self.website = None

    def load(self, projects):
        """
        Load data of a project.

        @param projects: Projects collection.
        @type  projects: L{Projects}
        """
        cfg_name = projects.get_projectdir(self.dir_name)
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

            pd = ProjectData(name)
            pd.load(self)
            self.projects[name] = pd

projects = Projects()
