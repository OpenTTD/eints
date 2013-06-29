"""
Configuration and global routines of the translator service.
"""
import os, sys, glob
from webtranslate import data, loader
from webtranslate.newgrf import language_info

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
    return loader.collect_text_DOM(child).strip()

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

        cfg = loader.load_dom(self.config_path)
        cfg = loader.get_single_child_node(cfg, 'config')

        self.project_root = get_subnode_text(cfg, 'project-root')
        if self.project_root is None or self.project_root == "":
            print("No project root found, aborting!")
            sys.exit(1)

        self.language_file_size = data.convert_num(get_subnode_text(cfg, 'language-file-size'), self.language_file_size)
        self.num_backup_files   = data.convert_num(get_subnode_text(cfg, 'num-backup-files'),   self.num_backup_files)
        if self.num_backup_files > 100: self.num_backup_files = 100 # To limit it two numbers in backup files.

        self.max_number_changes = data.convert_num(get_subnode_text(cfg, 'max-num-changes'), self.max_number_changes)
        self.min_number_changes = data.convert_num(get_subnode_text(cfg, 'min-num-changes'), self.min_number_changes)
        if self.min_number_changes < 1: self.min_number_changes = 1 # You do want to keep the latest version.
        self.change_stabilizing_time = data.convert_num(get_subnode_text(cfg, 'change-stable-age'), self.change_stabilizing_time)

        cache_size = data.convert_num(get_subnode_text(cfg, 'project-cache'), 10)
        cache.init(self.project_root, cache_size)

        # Redmine configuration.
        rm_node = loader.get_single_child_node(cfg, 'redmine', True)
        if rm_node is not None:
            from webtranslate.users import redmine
            # Initialize the redmine fields.
            redmine.db_type = None
            redmine.db_schema = None
            redmine.db_name = None
            redmine.db_user = None
            redmine.db_password = None
            redmine.db_host = None
            redmine.db_port = None
            redmine.owner_role = None
            redmine.translator_roles = {}

            redmine.db_type = get_subnode_text(rm_node, 'db-type')
            if redmine.db_type not in ('postgress', 'mysql', 'sqlite3'):
                print("Unknown db type in config, aborting!")
                sys.exit(1)
            redmine.db_schema = get_subnode_text(rm_node, 'db-schema')
            redmine.db_name = get_subnode_text(rm_node, 'db-name')
            redmine.db_user = get_subnode_text(rm_node, 'db-user')
            redmine.db_password = get_subnode_text(rm_node, 'db-password')
            redmine.db_host = get_subnode_text(rm_node, 'db-host')
            redmine.db_port = data.convert_num(get_subnode_text(rm_node, 'db-port'), None)
            redmine.owner_role = get_subnode_text(rm_node, 'owner-role')

            iso_codes = set(li.isocode for li in language_info.all_languages)
            for node in loader.get_child_nodes(rm_node, 'translator-role'):
                iso_code = node.getAttribute('language')
                if iso_code not in iso_codes:
                    print("Language \"" + iso_code + "\" in translator roles is not known, ignored the entry.")
                    continue
                if iso_code in redmine.translator_roles:
                    print("Language \"" + iso_code + "\" in translator roles is already defined, ignoring the other entry.")
                    continue
                redmine.translator_roles[iso_code] = loader.collect_text_DOM(node).strip()

            # Do some sanity checking.
            if redmine.db_schema == "": redmine.db_schema = None
            if redmine.db_name == "" or redmine.db_user == "" or redmine.db_host == "" or redmine.db_port == None or redmine.db_port == 0:
                redmine.db_name = None
                redmine.db_user = None
                redmine.db_password = None
                redmine.db_host = None
                redmine.db_port = None

            if redmine.owner_role == "": redmine.owner_role = None
            for iso_code, role_name in list(redmine.translator_roles.items()):
                if role_name == "": del redmine.translator_roles[iso_code]




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

    def create_project(self, disk_name, human_name, url):
        """
        Create a new project.

        @param disk_name: Base name of the project at the disk.
        @type  disk_name: C{str}

        @param human_name: Project name for humans.
        @type  human_name: C{str}

        @return: Error description, or nothing if creation succeeded.
        @rtype:  C{str} or C{None}
        """
        if disk_name in self.projects:
            return "A project named \"{}\" already exists".format(disk_name)

        path =  os.path.join(self.project_root, disk_name)
        if os.path.exists(path + ".xml"):
            return "A project file named \"{}\" already exists".format(disk_name)

        # Construct a new project from scratch.
        pmd = ProjectMetaData(path, disk_name, human_name)
        self.projects[disk_name] = pmd
        pmd.pdata = data.Project(human_name, url)
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
            return pmd

        # Load the data, first make some room.
        size = len(self.lru)
        i = size - 1
        while size >= self.cache_size and i >= 0:
            # XXX If project is locked, skip it.
            assert self.lru[i].pdata is not None
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

    @ivar human_name: Project name for humans.
    @type human_name: C{str}

    @ivar path: Path of the project file at disk (without extension.
    @type path: C{str}
    """
    def __init__(self, path, disk_name, human_name=None):
        self.pdata = None
        self.name = disk_name
        self.overview = {}
        if human_name is not None:
            self.human_name = human_name
        else:
            # The project has the actual human-readable name, and will be stored here on first load.
            self.human_name = disk_name
        self.path = path

    def load(self):
        assert self.pdata is None
        self.pdata = data.load_file(self.path + ".xml")
        process_project_changes(self.pdata)
        self.human_name = self.pdata.human_name # Copy the human-readable name from the project data.

    def unload(self):
        # XXX Unlink the data
        self.pdata = None

    def save(self):
        """
        Save project data into an xml file, and manage the backup files.
        """
        base_path = self.path + ".xml"
        bpl = len(base_path) + 1 # "projname.xml." + "<something>"

        # Find current set of data files.
        data_files = {}
        if os.path.exists(base_path):
            data_files[None] = base_path

        for fname in glob.glob(base_path + ".*"):
            extname = fname[bpl:]
            if extname.startswith("bup"):
                num = data.convert_num(extname[3:], None)
                if num is not None: data_files[num] = fname

        data.save_file(self.pdata, self.path + ".xml.new")

        # Generate mv and rm commands for the data files.
        cmds = [('mv', self.path + ".xml.new", base_path)]
        last, num = None, 1
        while num <= cfg.num_backup_files and num < 100 and last in data_files:
            new_name = base_path + ".bup{:02d}".format(num)
            cmds.append(('mv', data_files[last], new_name))
            del data_files[last]
            last = num
            num = num + 1
        for fname in data_files.values():
            cmds.append(('rm', fname))

        # Execute the commands.
        cmds.reverse()
        for cmd in cmds:
            if cmd[0] == 'mv':
                os.rename(cmd[1], cmd[2])
            elif cmd[0] == 'rm':
                os.unlink(cmd[1])


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


def process_changes(lchgs, cases, stamp, used_basetexts):
    """
    Check whether the changes should all still be kept.

    @param lchgs: Language changes of a string.
    @type  lchgs: C{list} of L{Change}

    @param cases: Cases of the language.
    @type  cases: C{list} of C{str}

    @param stamp: Current moment in time.
    @type  stamp: L{Stamp}

    @param used_basetexts: Collected base texts in the kept language changes.
    @type  used_basetexts: C{set} of L{Text}

    @return: Updated changes. If the length has not changed, they are still the same.
    @rtype:  C{list} of L{Change}
    """
    lchgs.sort()
    cases = dict((c, 0) for c in cases)
    newchgs = []
    for chg in reversed(lchgs):
        n = cases[chg.case]
        if n < cfg.min_number_changes or \
                (stamp.seconds - chg.stamp.seconds < cfg.change_stabilizing_time and n <= cfg.max_number_changes):
            # Not enough changes collected yet for this case.
            # Not old enough, and not enough to throw them away.
            newchgs.append(chg)
            cases[chg.case] = n + 1
            used_basetexts.add(chg.base_text)

    return newchgs

def process_project_changes(pdata):
    """
    Update the changes of the texts in the project.

    @param pdata: Project data to examine and change.
    @type  pdata: L{Project}

    @return: Changes were changed.
    @rtype:  C{bool}
    """
    used_basetexts = set()
    stamp = data.make_stamp()
    modified = False
    if pdata.base_language is None: return # No base language -> nothing to do.
    # Update translation changes.
    for lname, lng in pdata.languages.items():
        if lname == pdata.base_language: continue
        for chgs in lng.changes.values():
            nchgs = process_changes(chgs, lng.case, stamp, used_basetexts)
            if len(nchgs) != len(chgs):
                chgs[:] = nchgs
                modified = True

    # Update base language changes.
    blng = pdata.languages[pdata.base_language]
    for chgs in blng.changes.values():
        chgs.sort()
        nchgs = []
        changed = False
        first = True
        for chg in reversed(chgs):
            if first or chg.base_text in used_basetexts:
                nchgs.append(chg)
                first = False
            else:
                changed = True

        if changed:
            chgs[:] = nchgs
            modified = True

    return modified


cfg = None
cache = ProjectCache()
