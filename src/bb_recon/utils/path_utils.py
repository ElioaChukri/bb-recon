from pathlib import Path


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


PROJECT_ROOT = _resolve_project_root()
DB_INIT_SCRIPT_PATH = PROJECT_ROOT / "db_schema" / "00_init_db.sql"
CONFIGS_PATH = PROJECT_ROOT / "configs"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "bb-recon"
SQLITE_DB_PATH = DEFAULT_DATA_DIR / "bb_recon.db"
