"""
Configuration and global routines of the translator service.
"""
import os
from webtranslate import data, loader

class Config:
    """
    Service configuration.

    @ivar project_root: Root directory of the web translation service.
    @type project_root: C{str}

    @ivar language_file_size: Maximum accepted file size of a language file.
    @type language_file_size: C{int}
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.language_file_size = 10000
        self.project_root = None

    def load_fromxml(self):
        if not os.path.isfile(self.config_path):
            print("Cannot find configuration file " + self.config_path)
            return

        # XXX Flush project cache too (when starting, the cache is still empty).

        data = loader.load_dom(self.config_path)
        cfg = loader.get_single_child_node(data, 'config')

        self.project_root = loader.collect_text_DOM(loader.get_single_child_node(cfg, 'project-root'))
        self.language_file_size = int(loader.collect_text_DOM(loader.get_single_child_node(cfg, 'language-file-size')))

        cache_size = int(loader.collect_text_DOM(loader.get_single_child_node(cfg, 'project-cache')))
        cache.init(self.project_root, cache_size)


class ProjectCache:
    """
    Cache for project data.

    @ivar project_root: Root of the projects.
    @type project_root: C{str}

    @ivar cache_size: Number of cached projects.
    @type cache_size: C{int}

    @ivar projects: Known projects ordered by name.
    @type projects: C{dict} of C{str} to L{ProjectMetaData}

    @ivar lru: LRU storage of loaded projects.
    @type lru: C{list} of L{ProjectMetaData}
    """
    def __init__(self):
        self.project_root = None
        self.cache_size = 0 # Disable cache
        self.projects = {}
        self.lru = []

    def init(self, project_root, cache_size):
        self.project_root = os.path.join(project_root, 'projects')
        self.cache_size = cache_size
        self.projects = {}
        self.lru = []

        for name in os.listdir(self.project_root):
            if not name.endswith('.xml'): continue
            name = name[:4]
            path = os.path.join(self.project_root, name)
            pmd = ProjectMetaData(path, name)
            assert name not in self.projects
            self.projects[name] = pmd

            pd = self.get_pmd(name)
            assert pd is pmd
            pd = pd.pdata

            pmd.proj_name = pd.name

    def get_pmd(self, proj_name):
        """
        Load a project.

        @param proj_name: Name of the project (filename without .xml extension)
        @type  proj_name: C{str}

        @return: The project, or C{None}
        @rtype:  L{ProjectMetaData} or C{None}
        """
        # Does it exist?
        pmd = self.projects.get(proj_name)
        if pmd is None:
            print("ERROR: Retrieving project " + proj_name)
            return None

        # Is it loaded?
        if pmd.pdata is not None:
            lru = [pmd]
            for p in self.lru:
                if p != pmd: lru.append(p)
            assert len(lru) == len(self.lru)
            self.lru = lru
            print("Retrieving project " + pmd.path + " from cache")
            return pmd

        # Load the data, first make some room.
        size = len(self.lru)
        i = size - 1
        while size >= self.cache_size and i >= 0:
            # XXX If project is locked, skip it.
            assert self.lru[i].pdata is not None
            print("Dropping project " + self.lru[i].pdata.path)
            self.lru[i].unload()
            self.lru[i] = None
            size = size - 1
            i = i - 1

        # Shuffle project to the front in the lru cache, and drop the removed entries.
        # XXX We should compute beforehand, whether there is space in the lru
        # XXX to add the requested project.
        lru = [pmd]
        for p in self.lru:
            if p is not None: lru.append(p)
        self.lru = lru

        pmd.load()
        print("Loading project " + pmd.path)
        return pmd

    def save_pmd(self, pmd):
        """
        Save the project.

        @param pmd: Project meta data.
        @type  pmd: L{ProjectMetaData}
        """
        pmd.save()



class ProjectMetaData:
    """
    Some project meta data for the translation service.

    @ivar pdata: Project data if it is loaded in memory.
    @type pdata: C{None} or L{Project}

    @ivar name: Name of the project (basename).
    @type name: C{str}

    @ivar proj_name: Project name for humans.
    @type proj_name: C{str}

    @ivar path: Path of the project file at disk (without extension.
    @type path: C{str}
    """
    def __init__(self, path, name):
        self.pdata = None
        self.name = name
        self.proj_name = name # Temporary
        self.path = path

    def load(self):
        assert self.pdata is None
        self.pdata = data.load_file(self.path + ".xml")

    def unload(self):
        # XXX Unlink the data
        self.pdata = None

    def save(self):
        print("Save project to " + self.path)
        data.save_file(self.pdata, self.path + ".xml.new")


cfg = None
cache = ProjectCache()
