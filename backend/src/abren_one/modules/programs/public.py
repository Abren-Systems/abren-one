"""Public interface for the Programs module (§3.1, §3.4).

Other modules must import ONLY from this file.
"""

from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
    CreateProgramResult,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.exceptions import (
    ProgramError,
    ProgramNotFoundError,
    ProjectNotFoundError,
)
from abren_one.modules.programs.application.queries.get_program import (
    GetProgramResult,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.list_programs import (
    ProgramSummaryResult,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)

__all__ = [
    "CreateProgramInput",
    "CreateProgramResult",
    "GetProgramResult",
    "ProgramError",
    "ProgramNotFoundError",
    "ProgramSummaryResult",
    "ProjectNotFoundError",
    "create_program",
    "get_program",
    "list_programs",
]
