"""
Configuration and global routines of the translator service.
"""
import os
import sys
from webtranslate import data, loader, project_type
from webtranslate.newgrf import language_info, language_file

# Recognized types of project disk storage.
STORAGE_ONE_FILE = "One large file for the entire project"
STORAGE_SEPARATE_LANGUAGES = "Directory with project_data.[xml|json] and a set of language files"


class ProjectStorage:
    """
    @ivar path: Path to the base of the stored project.
                For C{STORAGE_ONE_FILE}, the path is the name of the .[xml|json] file.
                For C{STORAGE_SEPARATE_LANGUAGES}, the path is the directory path.
    @type path: C{str}

    @ivar name: Name of the project (basename at the disk).
    @type name: C{str}

    @ivar languages: Detected language files of the project. Always empty for L{STORAGE_ONE_FILE}.
    @type languages: C{list} of C{str}

    @ivar storage_type: Type of storage of the project at the disk.
    @type storage_type: One of L{STORAGE_ONE_FILE} or L{STORAGE_SEPARATE_LANGUAGES}

    @ivar data_format: Used data format.
    @type data_format: C{str} (C{xml} or C{json}
    """

    def __init__(self, path, name, languages, storage_type, data_format):
        self.path = path
        self.name = name
        self.languages = languages
        self.storage_type = storage_type
        self.data_format = data_format


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

    @ivar server_mode: Mode of the server, either C{'development'} or C{'production'}
                       for the bottle server, or C{'mod_wsgi'} for mod_wsgi.
    @type server_mode: C{str}

    @ivar server_host: Hostname of the server to bind to.
    @type server_host: C{str}

    @ivar server_port: Port number of the server host.
    @type server_port: C{int}

    @ivar authentication: Method of authentication, either C{'development'}. C{'redmine'}, C{'github'} or C{'ldap'}.
    @type authentication: C{str}

    @ivar stable_languages_path: Directory for meta data files of stable languages.
    @type stable_languages_path: C{str} or C{None}

    @ivar unstable_languages_path: Directory for meta data files of unstable languages (lacking sufficient translators).
    @type unstable_languages_path: C{str} or C{None}

    @ivar project_root: Root directory of the web translation service.
    @type project_root: C{str}

    @ivar language_file_size: Maximum accepted file size of a language file.
    @type language_file_size: C{int}

    @ivar project_types: Project types that are acceptable to the web translation.
    @type project_types: C{set} of C{str}

    @ivar storage_format: Preferred storage format at the disk.
    @type storage_format: One of C{STORAGE_ONE_FILE} or C{STORAGE_SEPARATE_LANGUAGES}

    @ivar data_format: Data format of the files.
    @type data_format: C{str}, C{xml} or C{json}

    @ivar num_backup_files: Number of backup files kept for a project.
    @type num_backup_files: C{int}

    @ivar max_number_changes: Maximum number of changes that should be kept for
                              a string in a translation.
    @type max_number_changes: C{int}

    @ivar min_number_changes: Minimum number of changes that should be kept for
                              a string in a translation.
    @type min_number_changes: C{int}

    @ivar change_stabilizing_time: Amount of seconds needed before a change
                                   can be considered old enough to discard.
    @type change_stabilizing_time: C{int}
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.language_file_size = 10000
        self.stable_languages_path = None
        self.unstable_languages_path = None
        self.project_root = None
        self.num_backup_files = 5
        self.max_number_changes = 5
        self.min_number_changes = 1
        self.change_stabilizing_time = 1000000  # 11 days, 13 hours, 46 minutes, and 40 seconds.
        self.data_format = "xml"

    def load_settings_from_xml(self):
        """
        Load the 'config.xml' settings into the configuration, mostly paths to find other data.
        """
        if not os.path.isfile(self.config_path):
            print("Cannot find configuration file " + self.config_path)
            return

        cfg = loader.load_dom(self.config_path)
        cfg = loader.get_single_child_node(cfg, "config")

        self.server_mode = get_subnode_text(cfg, "server-mode")
        if self.server_mode not in ("development", "production", "mod_wsgi"):
            print("Incorrect server-mode in the configuration, aborting!")
            sys.exit(1)

        self.server_host = get_subnode_text(cfg, "server-host")
        self.server_port = data.convert_num(get_subnode_text(cfg, "server-port"), 80)
        self.authentication = get_subnode_text(cfg, "authentication")
        if self.authentication not in ("development", "redmine", "github", "ldap"):
            print("Incorrect authentication in the configuration, aborting!")
            sys.exit(1)

        self.stable_languages_path = get_subnode_text(cfg, "stable-languages")
        if self.stable_languages_path == "":
            self.stable_languages_path = None

        self.unstable_languages_path = get_subnode_text(cfg, "unstable-languages")
        if self.unstable_languages_path == "":
            self.unstable_languages_path = None

        self.project_root = get_subnode_text(cfg, "project-root")
        if self.project_root is None or self.project_root == "":
            print("No project root found, aborting!")
            sys.exit(1)

        self.project_types = get_subnode_text(cfg, "project-types").split()
        self.project_types = set(ptype for ptype in self.project_types if ptype in project_type.project_types)
        if len(self.project_types) == 0:
            print("No valid project types found, aborting!")
            sys.exit(1)

        storage_type = get_subnode_text(cfg, "storage-format").strip()
        if storage_type == "one-file":
            self.storage_format = STORAGE_ONE_FILE
        elif storage_type == "split-languages":
            self.storage_format = STORAGE_SEPARATE_LANGUAGES
        else:
            print('Unrecognized preferred storage format "{}", aborting!'.format(storage_type))
            sys.exit(1)

        self.data_format = get_subnode_text(cfg, "data-format").strip()
        if self.data_format not in ("xml", "json"):
            self.data_format = "xml"

        self.language_file_size = data.convert_num(get_subnode_text(cfg, "language-file-size"), self.language_file_size)
        self.num_backup_files = data.convert_num(get_subnode_text(cfg, "num-backup-files"), self.num_backup_files)
        # To limit it two digits in backup files.
        if self.num_backup_files > 100:
            self.num_backup_files = 100

        self.max_number_changes = data.convert_num(get_subnode_text(cfg, "max-num-changes"), self.max_number_changes)
        self.min_number_changes = data.convert_num(get_subnode_text(cfg, "min-num-changes"), self.min_number_changes)
        # You do want to keep the latest version.
        if self.min_number_changes < 1:
            self.min_number_changes = 1

        self.change_stabilizing_time = data.convert_num(
            get_subnode_text(cfg, "change-stable-age"), self.change_stabilizing_time
        )

        cache_size = data.convert_num(get_subnode_text(cfg, "project-cache"), 10)
        cache.init(self.project_root, cache_size)

    def load_userauth_from_xml(self):
        """
        Load 'redmine', 'github' and 'ldap' authentication if they exist.
        """
        if not os.path.isfile(self.config_path):
            print("Cannot find configuration file " + self.config_path)
            return

        cfg = loader.load_dom(self.config_path)
        cfg = loader.get_single_child_node(cfg, "config")

        # Redmine configuration.
        rm_node = loader.get_single_child_node(cfg, "redmine", True)
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

            redmine.db_type = get_subnode_text(rm_node, "db-type")
            if redmine.db_type not in ("postgress", "mysql", "sqlite3"):
                print("Unknown db type in config, aborting!")
                sys.exit(1)
            redmine.db_schema = get_subnode_text(rm_node, "db-schema")
            redmine.db_name = get_subnode_text(rm_node, "db-name")
            redmine.db_user = get_subnode_text(rm_node, "db-user")
            redmine.db_password = get_subnode_text(rm_node, "db-password")
            redmine.db_host = get_subnode_text(rm_node, "db-host")
            redmine.db_port = data.convert_num(get_subnode_text(rm_node, "db-port"), None)
            redmine.owner_role = get_subnode_text(rm_node, "owner-role")

            iso_codes = set(li.isocode for li in language_info.all_languages)
            for node in loader.get_child_nodes(rm_node, "translator-role"):
                iso_code = node.getAttribute("language")
                if iso_code not in iso_codes:
                    print('Language "' + iso_code + '" in translator roles is not known, ignored the entry.')
                    continue
                if iso_code in redmine.translator_roles:
                    print(
                        'Language "' + iso_code + '" in translator roles is already defined, ignoring the other entry.'
                    )
                    continue
                redmine.translator_roles[iso_code] = loader.collect_text_DOM(node).strip()

            # Do some sanity checking.
            if redmine.db_schema == "":
                redmine.db_schema = None
            if (
                redmine.db_name == ""
                or redmine.db_user == ""
                or redmine.db_host == ""
                or redmine.db_port is None
                or redmine.db_port == 0
            ):
                redmine.db_name = None
                redmine.db_user = None
                redmine.db_password = None
                redmine.db_host = None
                redmine.db_port = None

            if redmine.owner_role == "":
                redmine.owner_role = None
            for iso_code, role_name in list(redmine.translator_roles.items()):
                if role_name == "":
                    del redmine.translator_roles[iso_code]

        # github configuration.
        gh_node = loader.get_single_child_node(cfg, "github", True)
        if gh_node is not None:
            from webtranslate.users import github
            from webtranslate import protect

            github.github_org_api_token = get_subnode_text(gh_node, "org-api-token")
            github.github_organization = get_subnode_text(gh_node, "organization")
            github.github_oauth_client_id = get_subnode_text(gh_node, "oauth2-client-id")
            github.github_oauth_client_secret = get_subnode_text(gh_node, "oauth2-client-secret")
            protect.translators_password = get_subnode_text(gh_node, "translators-password")

        # Ldap configuration
        ldap_node = loader.get_single_child_node(cfg, "ldap", True)
        if ldap_node is not None:
            from webtranslate.users import ldap

            # Initialize the ldap fields.
            ldap.ldap_host = None
            ldap.ldap_basedn_users = None
            ldap.ldap_basedn_groups = None
            ldap.owner_group = None
            ldap.translator_groups = {}

            ldap.ldap_host = get_subnode_text(ldap_node, "host")
            ldap.ldap_basedn_users = get_subnode_text(ldap_node, "basedn-users")
            ldap.ldap_basedn_groups = get_subnode_text(ldap_node, "basedn-groups")

            ldap.owner_group = get_subnode_text(ldap_node, "owner-group")

            iso_codes = set(li.isocode for li in language_info.all_languages)
            for node in loader.get_child_nodes(ldap_node, "translator-group"):
                iso_code = node.getAttribute("language")
                if iso_code not in iso_codes:
                    print('Language "' + iso_code + '" in translator groups is not known, ignored the entry.')
                    continue
                if iso_code in ldap.translator_groups:
                    print(
                        'Language "' + iso_code + '" in translator groups is already defined, ignoring the other entry.'
                    )
                    continue
                ldap.translator_groups[iso_code] = loader.collect_text_DOM(node).strip()

            # Do some sanity checking.
            if ldap.ldap_host == "":
                ldap.ldap_host = None

            if ldap.owner_group == "":
                ldap.owner_group = None
            for iso_code, group_name in list(ldap.translator_groups.items()):
                if group_name == "":
                    del ldap.translator_groups[iso_code]


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
        self.cache_size = 0  # Disable cache
        self.projects = {}
        self.lru = []

    def init(self, project_root, cache_size):
        """
        Initialize the project cache.

        @param project_root: Root directory of the projects.
        @type  project_root: C{str}

        @param cache_size: Maximum number of cached projects.
        @type  cache_size: C{str}
        """
        self.project_root = project_root
        self.cache_size = cache_size
        self.projects = {}
        self.lru = []

    def find_projects(self):
        """
        Examine the disk for translation projects and create stubs for them.
        """
        for proj in find_project_files(self.project_root):
            self.projects[proj.name] = ProjectMetaData(proj)
            self.get_pmd(proj.name)

    def create_project(self, disk_name, human_name, projtype, url):
        """
        Create a new project.

        @param disk_name: Base name of the project at the disk.
        @type  disk_name: C{str}

        @param human_name: Project name for humans.
        @type  human_name: C{str}

        @param projtype: Project type.
        @type  projtype: L{ProjectType}

        @param url: Web address of the project, or empty.
        @type  url: C{str}

        @return: Error description, or nothing if creation succeeded.
        @rtype:  C{str} or C{None}
        """
        if disk_name in self.projects:
            return 'A project named "{}" already exists'.format(disk_name)

        if not may_create_project(self.project_root, disk_name):
            return 'A project file named "{}" already exists'.format(disk_name)

        # Construct a new project from scratch.
        storage = cfg.storage_format
        if storage == STORAGE_ONE_FILE:
            path = os.path.join(self.project_root, disk_name + "." + cfg.data_format)
        else:
            path = os.path.join(self.project_root, disk_name)
            if not os.path.isdir(path):
                assert not os.path.exists(path)
                os.mkdir(path)

        proj_store = ProjectStorage(path, disk_name, [], cfg.storage_format, cfg.data_format)
        pmd = ProjectMetaData(proj_store, human_name)
        self.projects[disk_name] = pmd
        pmd.pdata = data.Project(human_name, projtype, url)
        pmd.pdata.set_modified()
        pmd.create_statistics()
        self.lru.append(pmd)
        self.save_pmd(pmd)
        return None

    def get_pmd(self, proj_name):
        """
        Load a project.

        @param proj_name: Name of the project (filename without extension)
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
                if p != pmd:
                    lru.append(p)
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
            if p is not None:
                lru.append(p)
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
                    Entries also define the set of languages to load in case L{storage_format} is
                    L{STORAGE_SEPARATE_LANGUAGES}.
    @type overview: C{dict} of C{str} to C{list} of C{int}

    @ivar string_avoid_cache: Cache to store which strings to avoid for translating, ordered by
                              language.
    @type string_avoid_cache: C{dict} of C{str} to L{StringAvoidanceCache}

    @ivar blang_name: Name of base language, if any.
    @type blang_name: C{None} or C{str}

    @ivar blang_count: Number of strings in base language.
    @type blang_count: C{int}

    @ivar human_name: Project name for humans.
    @type human_name: C{str}

    @ivar path: Path of the project file at disk (with extension).
    @type path: C{str}

    @ivar storage_type: Files used to store the project.
    @type storage_type: C{str}, either L{STORAGE_ONE_FILE} or L{STORAGE_SEPARATE_LANGUAGES}

    @ivar data_format: Data format used to store the data.
    @type data_format: C{str}, either 'xml', or 'json'
    """

    def __init__(self, proj_store, human_name=None):
        self.pdata = None
        self.name = proj_store.name

        self.overview = {}
        if proj_store.storage_type == STORAGE_SEPARATE_LANGUAGES:
            for lng_name in proj_store.languages:
                self.overview[lng_name] = [0, 0, 0, 0, 0]

        self.string_avoid_cache = {}
        self.blang_name = None
        self.blang_count = 0
        if human_name is not None:
            self.human_name = human_name
        else:
            # The project has the actual human-readable name, and will be stored here on first load.
            self.human_name = proj_store.name

        self.path = proj_store.path
        self.storage_type = proj_store.storage_type
        self.data_format = proj_store.data_format

        if self.storage_type == STORAGE_SEPARATE_LANGUAGES:
            assert not self.path.endswith(".xml") and not self.path.endswith(".json")
        else:
            assert self.storage_type == STORAGE_ONE_FILE
            assert self.path.endswith(".xml") or self.path.endswith(".json")

    def load(self):
        assert self.pdata is None

        if self.storage_type == STORAGE_ONE_FILE:
            if self.data_format == "xml":
                xloader = data.XmlLoader(False)
            else:
                xloader = data.JsonLoader(False)

            del self.pdata
            self.pdata = xloader.load_project(self.path)
        else:
            assert self.storage_type == STORAGE_SEPARATE_LANGUAGES
            if self.data_format == "xml":
                xloader = data.XmlLoader(True)
            else:
                xloader = data.JsonLoader(True)

            del self.pdata
            self.pdata = xloader.load_project(os.path.join(self.path, "project_data." + self.data_format))
            for lng_name in self.overview:
                path = os.path.join(self.path, lng_name + "." + self.data_format)
                self.pdata.languages[lng_name] = xloader.load_language(self.pdata.projtype, path)

            # Check that we have a base language, else drop translations.
            project = self.pdata
            if project.get_base_language() is None:
                project.base_language = None
                if len(self.pdata.languages) > 0:
                    print('Project "' + project.human_name + '" has no base language, dropping all translations')
                project.languages = {}

        process_project_changes(self.pdata)
        self.human_name = self.pdata.human_name  # Copy the human-readable name from the project data.

    def unload(self):
        # XXX Unlink the data
        self.pdata = None

    def save(self):
        """
        Save project data into a data file, and manage the backup files.
        """
        if self.storage_type == STORAGE_ONE_FILE:
            needs_save = self.pdata.modified
            if not needs_save:
                for lng in self.pdata.languages.values():
                    if lng.modified:
                        needs_save = True
                        break

            if needs_save:
                if self.data_format == "xml":
                    xsaver = data.XmlSaver(False, True)
                else:
                    xsaver = data.JsonSaver(False)

                xsaver.save_project(self.pdata, self.path + ".new")
                rotate_files(self.path)

                self.pdata.modified = False
                for lng in self.pdata.languages.values():
                    lng.modified = False
        else:
            # Project directory should already exist, created as part of project creation.
            assert self.storage_type == STORAGE_SEPARATE_LANGUAGES
            if self.data_format == "xml":
                xsaver = data.XmlSaver(True, False)
            else:
                xsaver = data.JsonSaver(True)

            if self.pdata.modified:
                path = os.path.join(self.path, "project_data." + self.data_format)
                xsaver.save_project(self.pdata, path + ".new")
                rotate_files(path)
                self.pdata.modified = False

            for lng in self.pdata.languages.values():
                if lng.modified:
                    path = os.path.join(self.path, lng.name + "." + self.data_format)
                    xsaver.save_language(self.pdata.projtype, lng, path + ".new")
                    rotate_files(path)
                    lng.modified = False

    def create_statistics(self, parm_lng=None):
        """
        Construct overview statistics of the project.

        @param parm_lng: If specified only update the provided language. Otherwise, update all translations.
        @type  parm_lng: C{Language} or C{None}
        """
        pdata = self.pdata

        blng = pdata.get_base_language()
        if blng is None:
            return

        self.blang_name = blng.name
        self.blang_count = len(blng.changes)

        if parm_lng is None or parm_lng is blng:  # Update all languages.
            pdata.statistics = {}

        # Get the pdata.statistics[lname] map for the base language.
        bstat = pdata.statistics.get(pdata.base_language)
        if bstat is None:
            bstat = {}
            pdata.statistics[pdata.base_language] = bstat

        projtype = pdata.projtype

        # First construct detailed information in the project
        for sname, bchgs in blng.changes.items():
            # Check newest base language string.
            bchg = data.get_newest_change(bchgs, "")
            binfo = language_file.check_string(projtype, bchg.base_text.text, True, None, blng, True)
            if binfo.has_error:
                bstat[sname] = [("", data.INVALID)]
            else:
                bstat[sname] = [("", data.UP_TO_DATE)]

            if parm_lng is None or parm_lng is blng:  # Update all languages.
                lngs = pdata.languages.items()
            else:
                lngs = [(parm_lng.name, parm_lng)]  # Update just 'parm_lng'

            for lname, lng in lngs:
                assert projtype.allow_case or lng.case == [""]
                if lng is blng:
                    continue
                # Get the pdata.statistics[lname][sname] list.
                lstat = pdata.statistics.get(lname)
                if lstat is None:
                    lstat = {}
                    pdata.statistics[lname] = lstat
                sstat = lstat.get(sname)
                if sstat is None:
                    sstat = []
                    lstat[sname] = sstat

                if binfo is None:  # Base string is broken, cannot judge translations.
                    sstat[:] = [("", data.UNKNOWN)]
                    continue

                chgs = lng.changes.get(sname)
                if chgs is None:  # No translation at all
                    sstat[:] = [("", data.MISSING)]
                    continue

                chgs = data.get_all_newest_changes(chgs, lng.case)
                detailed_state = data.decide_all_string_status(projtype, bchg, chgs, lng, binfo)
                sstat[:] = sorted((c, se[0]) for c, se in detailed_state.items())

        # Construct overview statistics for each language.
        if parm_lng is None or parm_lng is blng:  # Update all languages.
            lngs = pdata.languages.items()
            self.overview = {}
        else:
            lngs = [(parm_lng.name, parm_lng)]  # Update just 'parm_lng'

        for lname, lng in lngs:
            # if lng is blng: continue
            counts = [0 for i in range(data.MAX_STATE)]
            for sname in blng.changes:
                state = max(s[1] for s in pdata.statistics[lname][sname])
                if state != data.MISSING_OK:
                    counts[state] = counts[state] + 1
            self.overview[lname] = counts


def find_project_files(root):
    """
    Find projects at the disk, starting from the L{root} directory.

    @param root: Root of the projects disk storage.
    @type  root: C{str}

    @return: Found projects.
    @rtype:  C{list} of L{ProjectStorage}

    @note: the L{ProjectStorage.languages} field is not used in case of L{STORAGE_ONE_FILE}.
    """
    projects = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            if name.endswith(".xml"):
                name = name[:-4]
                data_format = "xml"
            elif name.endswith(".json"):
                name = name[:-5]
                data_format = "json"
            else:
                continue

            projects.append(ProjectStorage(path, name, [], STORAGE_ONE_FILE, data_format))
            continue

        elif os.path.isdir(path):
            if name == "projects":
                # Ignore obsolete 'projects' sub-directory, projects should be moved.
                continue

            found_format = None
            found_languages = []
            for sub_name in os.listdir(path):
                if sub_name.endswith(".xml"):
                    sub_name = sub_name[:-4]
                    data_format = "xml"
                elif sub_name.endswith(".json"):
                    sub_name = sub_name[:-5]
                    data_format = "json"
                else:
                    continue

                if sub_name == "project_data":
                    found_format = data_format
                elif sub_name in language_info.isocode:
                    found_languages.append(sub_name)

            if found_format is not None:
                # Languages may be empty (in case the project has no base language).
                projects.append(ProjectStorage(path, name, found_languages, STORAGE_SEPARATE_LANGUAGES, found_format))

    pnames = {}
    found_error = False
    for p in projects:
        if p.name in pnames:
            msg = 'Error: Project "{}" exists twice (as "{}" and as "{}"), please fix.'
            msg = msg.format(p.name, p.path, pnames[p.name].path)
            print(msg)
            found_error = True

        pnames[p.name] = p

    if found_error:
        print("Aborting.")
        sys.exit(1)

    return projects


def may_create_project(root, name):
    """
    Can a project named L{name} be safely created at the disk?

    @param root: Root of the projects disk storage.
    @type  root: C{str}

    @param name: Name of the project.
    @type  name: C{str}

    @return: Whether a project with the provided name can be safely created.
    @rtype:  C{bool}
    """
    if name == "projects":  # Don't allow legacy directory name at all.
        return False

    path = os.path.join(root, name)

    # Does a L{STORAGE_ONE_FILE} project with the given name exists?
    if os.path.exists(path + ".xml") or os.path.exists(path + ".json"):
        return False

    # Does a L{STORAGE_SEPARATE_LANGUAGES} project with the give name exists?
    # Over-estimate, just name existence is sufficient reason to reject.
    if os.path.exists(path):
        return False

    return True


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
    lchgs.reverse()
    cases = dict((c, 0) for c in cases)
    newchgs = []
    done = set()
    # First round, copy what cannot be thrown out.
    for i in range(len(lchgs)):
        chg = lchgs[i]
        case_count = cases[chg.case]
        if chg.last_upload or (
            stamp.seconds - chg.stamp.seconds < cfg.change_stabilizing_time and case_count <= cfg.max_number_changes
        ):
            # Last uploaded change, or still too young to throw away.
            newchgs.append(chg)
            cases[chg.case] = case_count + 1
            used_basetexts.add(chg.base_text)
            done.add(i)
    # Second round, copy more if there is room.
    for i in range(len(lchgs)):
        chg = lchgs[i]
        if i in done:
            continue
        case_count = cases[chg.case]
        if case_count < cfg.min_number_changes:
            newchgs.append(chg)
            cases[chg.case] = case_count + 1
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
    if pdata.base_language is None:
        return False  # No base language -> nothing to do.

    # Update translation changes.
    for lname, lng in pdata.languages.items():
        if lname == pdata.base_language:
            continue
        lng_modified = False
        for chgs in lng.changes.values():
            nchgs = process_changes(chgs, lng.case, stamp, used_basetexts)
            if len(nchgs) != len(chgs):
                chgs[:] = nchgs
                modified = True
                lng_modified = True

        if lng_modified:
            lng.set_modified()

    # Update base language changes.
    blng = pdata.languages[pdata.base_language]
    blng_modified = False
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
            pdata.flush_related_cache()
            blng_modified = True

    if blng_modified:
        blng.set_modified()

    return modified


def rotate_files(fpath):
    """
    Rotate backup files of the provided filename path. It is assumed a C{fpath + ".new"} file exists
    to rotate in.

    @param fpath: Path of the file to rotate.
    @type  fpath: C{str}
    """
    dirname, filename = os.path.split(fpath)
    assert dirname != "" and filename != ""  # Assume it is a path with a / in it.

    data_files = {}
    new_name = filename + ".new"
    bup_name = filename + ".bup"
    for name in os.listdir(dirname):
        if not name.startswith(filename):
            continue

        path = os.path.join(dirname, name)
        if name == filename:
            data_files[0] = path

        elif name == new_name:
            data_files[-1] = path

        elif name.startswith(bup_name):
            num = data.convert_num(name[len(bup_name) :], None)
            if num is None or num <= 0:
                continue
            data_files[num] = path

    assert -1 in data_files  # We should have a '.new' file.
    missing = 0
    while missing in data_files and missing < 99 and missing < cfg.num_backup_files:
        missing = missing + 1

    cmds = []
    if missing in data_files:
        # Missing isn't really missing, loop ended due to upper bound check.
        # Remove the 'missing' file to make room.
        cmds.append(("rm", data_files[missing]))
    else:
        # 'missing' was really missing, add it so it can be used below.
        if missing == 0:
            data_files[missing] = os.path.join(dirname, filename)
        else:
            data_files[missing] = os.path.join(dirname, "{}{:02d}".format(bup_name, missing))

    # Generate mv and rm commands for the data files.
    num = missing - 1
    while num >= -1:
        cmds.append(("mv", data_files[num], data_files[num + 1]))
        num = num - 1
    for num, path in data_files.items():
        if num > cfg.num_backup_files:
            cmds.append(("rm", path))

    # Execute the commands.
    for cmd in cmds:
        if cmd[0] == "mv":
            os.rename(cmd[1], cmd[2])
        elif cmd[0] == "rm":
            os.unlink(cmd[1])


cfg = None
cache = ProjectCache()
