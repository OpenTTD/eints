"""
The type of project decides what language string primitives exist, and how they should be used.
"""

class ProjectType:
    """
    Base class of the project type.

    @ivar name: Name of the project type.
    @type name: C{str}

    @ivar human_name: Human readable name of the project type.
    @type human_name: C{str}
    """
    def __init__(self, name, human_name):
        self.name = name
        self.human_name = human_name

class NewGRFProject(ProjectType):
    """
    Project type for NewGRF strings.
    """
    def __init__(self):
        ProjectType.__init__(self,
            name = "newgrf",
            human_name = "NewGrf")

# Available project types, ordered by internal name.
project_types = {}
for pt in [NewGRFProject()]:
    project_types[pt.name] = pt

