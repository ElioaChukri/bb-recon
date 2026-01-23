import logging
import shlex
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def log_and_run(command: list[str], dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    """
    Log and run a subprocess command.
    :param command: The command to run as a list of strings.
    :param dry_run: If True, only log the command without executing it.
    :return: subprocess.CompletedProcess: The result of the command execution.
    """
    # Convert any Path objects in the command to strings
    command = [str(arg) if isinstance(arg, Path) else arg for arg in command]

    command_string = shlex.join(command)

    if dry_run:
        logger.info(f"Dry run enabled, would have run command: {command_string}")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    logger.info(f"Running command: {command_string}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Commad failed (exit {result.returncode}): {result.stderr.strip()}")
    else:
        logger.debug(f"Output: {result.stdout.strip()}")
    return result
