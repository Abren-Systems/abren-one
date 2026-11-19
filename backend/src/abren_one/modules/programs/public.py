"""Public interface for the Programs module (§3.1, §3.4).

Other modules must import ONLY from this file.
"""

from abren_one.modules.programs.application.commands.create_activity import (
    CreateActivityInput,
    CreateActivityResult,
)
from abren_one.modules.programs.application.commands.create_activity import (
    execute as create_activity,
)
from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
    CreateProgramResult,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.commands.create_project import (
    CreateProjectInput,
    CreateProjectResult,
)
from abren_one.modules.programs.application.commands.create_project import (
    execute as create_project,
)
from abren_one.modules.programs.application.commands.update_activity import (
    UpdateActivityInput,
    UpdateActivityResult,
)
from abren_one.modules.programs.application.commands.update_activity import (
    execute as update_activity,
)
from abren_one.modules.programs.application.commands.update_program import (
    UpdateProgramInput,
    UpdateProgramResult,
)
from abren_one.modules.programs.application.commands.update_program import (
    execute as update_program,
)
from abren_one.modules.programs.application.commands.update_project import (
    UpdateProjectInput,
    UpdateProjectResult,
)
from abren_one.modules.programs.application.commands.update_project import (
    execute as update_project,
)
from abren_one.modules.programs.application.exceptions import (
    ActivityNotFoundError,
    InvalidActivityTransitionError,
    InvalidProgramTransitionError,
    InvalidProjectTransitionError,
    ProgramError,
    ProgramNotFoundError,
    ProjectNotFoundError,
)
from abren_one.modules.programs.application.queries.get_activity import (
    GetActivityResult,
)
from abren_one.modules.programs.application.queries.get_activity import (
    execute as get_activity,
)
from abren_one.modules.programs.application.queries.get_program import (
    GetProgramResult,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.get_project import (
    GetProjectResult,
)
from abren_one.modules.programs.application.queries.get_project import (
    execute as get_project,
)
from abren_one.modules.programs.application.queries.list_activities import (
    ActivitySummaryResult,
)
from abren_one.modules.programs.application.queries.list_activities import (
    execute as list_activities,
)
from abren_one.modules.programs.application.queries.list_programs import (
    ProgramSummaryResult,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)
from abren_one.modules.programs.application.queries.list_projects import (
    ProjectSummaryResult,
)
from abren_one.modules.programs.application.queries.list_projects import (
    execute as list_projects,
)

__all__ = [
    "ActivityNotFoundError",
    "ActivitySummaryResult",
    "CreateActivityInput",
    "CreateActivityResult",
    "CreateProgramInput",
    "CreateProgramResult",
    "CreateProjectInput",
    "CreateProjectResult",
    "GetActivityResult",
    "GetProgramResult",
    "GetProjectResult",
    "InvalidActivityTransitionError",
    "InvalidProgramTransitionError",
    "InvalidProjectTransitionError",
    "ProgramError",
    "ProgramNotFoundError",
    "ProgramSummaryResult",
    "ProjectNotFoundError",
    "ProjectSummaryResult",
    "UpdateActivityInput",
    "UpdateActivityResult",
    "UpdateProgramInput",
    "UpdateProgramResult",
    "UpdateProjectInput",
    "UpdateProjectResult",
    "create_activity",
    "create_program",
    "create_project",
    "get_activity",
    "get_program",
    "get_project",
    "list_activities",
    "list_programs",
    "list_projects",
    "update_activity",
    "update_program",
    "update_project",
]
