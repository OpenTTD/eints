"""
Webtranslator configuration data.
"""
import os

class Config:
    """
    Main configuration.

    @ivar root_dir: Root of the project data.
    @type root_dir: C{str}
    """
    def __init__(self):
        self.root_dir = "root_dir"

    def get_users_file(self):
        """
        Get the file name of the users rights.

        @return: Name of the file with user data, or C{None}
        @rtype:  C{str} or C{None}
        """
        fname = os.path.join(self.root_dir, "users.dat")
        if not os.path.isfile(fname):
            print("Warning: Users file '{}' does not exist".format(fname))
            return None
        return fname

    def get_projects_dir(self):
        """
        Get the root directory of the translator projects.

        @return: Path to the projects root directory, or C{None}
        @rtype:  C{str} or C{None}
        """
        dname = os.path.join(self.root_dir, "projects")
        if not os.path.isdir(dname):
            print("Warning: Projects root '{}' does not exist".format(dname))
            return None
        return dname

config = Config()
