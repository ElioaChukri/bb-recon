from __future__ import annotations

import logging
import sqlite3
from pathlib import Path  # noqa: TC003
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from bb_recon.utils.path_utils import DB_INIT_SCRIPT_PATH, DEFAULT_DATA_DIR

logger = logging.getLogger(__name__)

DOMAIN_REGEX = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"

DomainName = Annotated[str, StringConstraints(pattern=DOMAIN_REGEX)]


class CliArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    target_domain: DomainName
    enumerate_subdomains: bool = False
    app_data_dir: Path = DEFAULT_DATA_DIR

    @field_validator("app_data_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        """
        Expand user and resolve the application data directory path.
        :param v: str | Path: The input path.
        :return: Path: The expanded and resolved path.
        """
        if v is None:
            return DEFAULT_DATA_DIR
        return Path(v).expanduser().resolve()

    @classmethod
    def from_args(cls) -> CliArgs:
        """
        Create an instance of CliArgs from parsed command-line arguments.
        :return: CliArgs: The created instance.
        """
        from ..args import parse_args

        args = parse_args()
        return cls(
            target_domain=args.target_domain,
            enumerate_subdomains=args.enumerate_subdomains,
            app_data_dir=args.app_data_dir,
        )

    @property
    def db_path(self) -> Path:
        """
        Get the path to the SQLite database file.
        :return: Path: The database file path.
        """
        return self.app_data_dir / "bb_recon.sqlite3"


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="forbid", frozen=True)
    telegram_bot_token: str = Field(
        ...,
        description="Telegram bot token for sending notifications.",
    )
    telegram_chat_id: str = Field(
        ...,
        description="Telegram chat ID for sending notifications.",
    )
    github_api_token: str = Field(
        ...,
        description="GitHub API token to send authenticated requests.",
    )
    shodan_api_key: str = Field(
        ...,
        description="Shodan API key for accessing Shodan services.",
    )


class ReconConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    cli: CliArgs
    env: EnvConfig

    @classmethod
    def load(cls) -> ReconConfig:
        """
        Load configuration from CLI arguments and environment variables.
        :return: ReconConfig: The loaded configuration instance.
        """
        # noinspection PyArgumentList
        env_config = EnvConfig()
        cli_args = CliArgs.from_args()

        return cls(cli=cli_args, env=env_config)

    def initialize_database(self) -> None:
        """
        Ensure the database file exists and is initialized.
        """
        _ensure_app_data_dir_exists(self.cli.app_data_dir)
        _ensure_database_initialized(self.cli.db_path)


def _ensure_app_data_dir_exists(data_dir: Path) -> None:
    """
    Ensure the application data directory exists.
    :param data_dir: Path: The application data directory path.
    :return: None
    """
    if not data_dir.exists():
        logger.debug(f"Creating application data directory at {data_dir}")
    data_dir.mkdir(parents=True, exist_ok=True)


def _ensure_database_initialized(db_path: Path) -> None:
    """
    Ensure the SQLite database is initialized with the required schema.
    :param db_path: Path: The path to the SQLite database file.
    :return: None
    """
    if not db_path.exists():
        logger.debug(f"Creating and initializing database at {db_path}")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(DB_INIT_SCRIPT_PATH.read_text())
