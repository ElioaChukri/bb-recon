import logging
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)

REQUIRED_COMMANDS = ["subfinder", "httpx", "dnsx"]


def _resolve_project_root() -> Path:
    """
    Iterate through parent directories to find the project root by locating 'pyproject.toml'.
    :return: Path: The resolved project root directory.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find 'pyproject.toml' in any parent directories.")


def check_if_required_commands_exist() -> bool:
    """
    Check if a command exists in the system PATH.

    :return: bool: True if all required commands are found, False otherwise.
    """
    missing_commands = [cmd for cmd in REQUIRED_COMMANDS if which(cmd) is None]
    if missing_commands:
        logger.error(f"Missing required commands: {', '.join(missing_commands)}")
        return False
    return True


PROJECT_ROOT = _resolve_project_root()
DB_INIT_SCRIPT_PATH = PROJECT_ROOT / "db_schema" / "00_init_db.sql"
CONFIGS_PATH = PROJECT_ROOT / "configs"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "bb-recon"
SQLITE_DB_PATH = DEFAULT_DATA_DIR / "bb_recon.db"
