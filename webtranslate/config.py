"""
Configuration and global routines of the translator service.
"""
import os, sys, re, glob
from webtranslate import data, loader

def get_subnode_text(node, tag):
    """
    Get the text of a child node of L{node}.

    @param node: Parent node of the node containing the text.
    @type  node: L{xml.dom.minidom.Node}

    @param tag: Name of the child node to retrieve.
    @type  tag: C{str}

    @return: The text in the child node.
    @rtype:  C{str}
    """
    child = loader.get_single_child_node(node, tag)
    if child is None:
        return ""
    return loader.collect_text_DOM(child)

def convert_num(txt, default):
    """
    Convert the number given in L{txt} to a numeric form.

    @param txt: Text containing the number.
    @type  txt: C{str}

    @param default: Default value, in case the L{txt} is not a number.
    @type  default: C{int} or C{None}

    @return: The numeric value of the number if it is convertable.
    @rtype:  C{int} or the provided default
    """
    m = re.match("\\d+$", txt)
    if not m: return default
    return int(txt, 10)


class Config:
    """
    Service configuration.

    @ivar project_root: Root directory of the web translation service.
    @type project_root: C{str}

    @ivar language_file_size: Maximum accepted file size of a language file.
    @type language_file_size: C{int}

    @ivar num_backup_files: Number of backup files kept for a project.
    @type num_backup_files: C{int}

    @ivar max_number_changes: Maximum number of changes that should be kept for a string in a translation.
    @type max_number_changes: C{int}

    @ivar min_number_changes: Minimum number of changes that should be kept for a string in a translation.
    @type min_number_changes: C{int}

    @ivar change_stabilizing_time: Amount of seconds needed before a change can be considered old enough to discard.
    @type change_stabilizing_time: C{int}
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.language_file_size = 10000
        self.project_root = None
        self.num_backup_files = 5
        self.max_number_changes = 5
        self.min_number_changes = 1
        self.change_stabilizing_time = 1000000 # 11 days, 13 hours, 46 minutes, and 40 seconds.

    def load_fromxml(self):
        if not os.path.isfile(self.config_path):
            print("Cannot find configuration file " + self.config_path)
            return

        data = loader.load_dom(self.config_path)
        cfg = loader.get_single_child_node(data, 'config')

        self.project_root = get_subnode_text(cfg, 'project-root')
        if self.project_root is None or self.project_root == "":
            print("No project root found, aborting!")
            sys.exit(1)

        self.language_file_size = convert_num(get_subnode_text(cfg, 'language-file-size'), self.language_file_size)
        self.num_backup_files   = convert_num(get_subnode_text(cfg, 'num-backup-files'),   self.num_backup_files)
        if self.num_backup_files > 100: self.num_backup_files = 100 # To limit it two numbers in backup files.

        self.max_number_changes = convert_num(get_subnode_text(cfg, 'max-num-changes'), self.max_number_changes)
        self.min_number_changes = convert_num(get_subnode_text(cfg, 'min-num-changes'), self.min_number_changes)
        if self.min_number_changes < 1: self.min_number_changes = 1 # You do want to keep the latest version.
        self.change_stabilizing_time = convert_num(get_subnode_text(cfg, 'change-stable-age'), self.change_stabilizing_time)

        cache_size = convert_num(get_subnode_text(cfg, 'project-cache'), 10)
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
            name = name[:-4]
            path = os.path.join(self.project_root, name)
            pmd = ProjectMetaData(path, name)
            assert name not in self.projects
            self.projects[name] = pmd

            pd = self.get_pmd(name)
            assert pd is pmd
            pd = pd.pdata

            pmd.proj_name = pd.name

    def create_project(self, disk_name, proj_name):
        """
        Create a new project.

        @param disk_name: Base name of the project at the disk.
        @type  disk_name: C{str}

        @param proj_name: Project name.
        @type  proj_name: C{str}

        @return: Error description, or nothing if creation succeeded.
        @rtype:  C{str} or C{None}
        """
        if disk_name in self.projects:
            return "A project named \"{}\" already exists".format(disk_name)

        path =  os.path.join(self.project_root, disk_name)
        if os.path.exists(path + ".xml"):
            return "A project file named \"{}\" already exists".format(disk_name)

        # Construct a new project from scratch.
        pmd = ProjectMetaData(path, proj_name)
        self.projects[disk_name] = pmd
        pmd.pdata = data.Project(proj_name)
        pmd.create_statistics()
        self.lru.append(pmd)
        self.save_pmd(pmd)
        return None

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
            print("Dropping project " + self.lru[i].path)
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
        pmd.create_statistics()
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

    @ivar overview: Overview of the state of the strings in each language, ordered by language name.
    @type overview: C{dict} of C{str} to [#UNKNOWN, #UP_TO_DATE, #OUT_OF_DATE, #INVALID, #MISSING]

    @ivar proj_name: Project name for humans.
    @type proj_name: C{str}

    @ivar path: Path of the project file at disk (without extension.
    @type path: C{str}
    """
    def __init__(self, path, name):
        self.pdata = None
        self.name = name
        self.overview = {}
        self.proj_name = name # Temporary
        self.path = path

    def load(self):
        assert self.pdata is None
        self.pdata = data.load_file(self.path + ".xml")

    def unload(self):
        # XXX Unlink the data
        self.pdata = None

    def save(self):
        base_path = self.path + ".xml"
        bpl = len(base_path) + 1 # "projname.xml." + "<something>"
        backup_files = []
        for fname in glob.glob(base_path + ".*"):
            extname = fname[bpl:]
            if extname.startswith("bup"):
                num = convert_num(extname[3:], None)
                if num is not None: backup_files.append((num, fname))
        backup_files.sort()
        if len(backup_files) > 0:
            new_num = (backup_files[-1][0] % 100) + 1
        else:
            new_num = 0
        if cfg.num_backup_files > 0: backup_files = backup_files[:-cfg.num_backup_files]
        for num, fname in backup_files:
            print("unlink " + fname)
            #os.unlink(fname)

        data.save_file(self.pdata, self.path + ".xml.new")
        if os.path.exists(base_path):
            print("Save project to " + self.path + " (renaming to {:02d})".format(new_num))
            os.rename(base_path, self.path + ".xml.bup{:02d}".format(new_num))
        os.rename(self.path + ".xml.new", base_path)


    def create_statistics(self, parm_lng = None):
        """
        Construct overview statistics of the project.

        @param parm_lng: If specified only update the provided language. Otherwise, update all translations.
        @type  parm_lng: C{Language} or C{None}
        """
        pdata = self.pdata

        blng = pdata.get_base_language()
        if blng is None: return


        if parm_lng is None or parm_lng is blng: # Update all languages.
            pdata.statistics = {}

        # Get the pdata.statistics[lname] map for the base language.
        bstat = pdata.statistics.get(pdata.base_language)
        if bstat is None:
            bstat = {}
            pdata.statistics[pdata.base_language] = bstat

        # First construct detailed information in the project
        for sname, bchgs in blng.changes.items():
            bchg = data.get_newest_change(bchgs, '')
            binfo = data.get_base_string_info(bchg.base_text.text, blng)
            if binfo:
                bstat[sname] = [('', data.UP_TO_DATE)]
            else:
                bstat[sname] = [('', data.INVALID)]

            if parm_lng is None or parm_lng is blng: # Update all languages.
                lngs = pdata.languages.items()
            else:
                lngs = [(parm_lng.name, parm_lng)] # Update just 'parm_lng'

            for lname, lng in lngs:
                if lng is blng: continue
                # Get the pdata.statistics[lname][sname] list.
                lstat = pdata.statistics.get(lname)
                if lstat is None:
                    lstat = {}
                    pdata.statistics[lname] = lstat
                sstat = lstat.get(sname)
                if sstat is None:
                    sstat = []
                    lstat[sname] = sstat

                if binfo is None: # Base string is broken, cannot judge translations.
                    sstat[:] = [('', data.UNKNOWN)]
                    continue

                chgs = lng.changes.get(sname)
                if chgs is None: # No translation at all
                    sstat[:] = [('', data.MISSING)]
                    continue

                chgs = data.get_all_newest_changes(chgs, lng.case)
                detailed_state = data.decide_all_string_status(bchg, chgs, lng, binfo)
                sstat[:] = sorted((c,se[0]) for c, se in detailed_state.items())

        # Construct overview statistics for each language.
        unknown = data.UNKNOWN
        if parm_lng is None or parm_lng is blng: # Update all languages.
            lngs = pdata.languages.items()
            self.overview = {}
        else:
            lngs = [(parm_lng.name, parm_lng)] # Update just 'parm_lng'

        for lname, lng in lngs:
            #if lng is blng: continue
            counts = [0, 0, 0, 0, 0] # UNKNOWN, UP_TO_DATE, OUT_OF_DATE, INVALID, MISSING
            for sname in blng.changes:
                state = max(s[1] for s in pdata.statistics[lname][sname])
                if state >= unknown: counts[state - unknown] = counts[state - unknown] + 1
            self.overview[lname] = counts



cfg = None
cache = ProjectCache()
