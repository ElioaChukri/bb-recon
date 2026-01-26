import logging
import selectors
import shlex
import subprocess
from pathlib import Path
from typing import TextIO, cast

logger = logging.getLogger(__name__)


def log_and_run(
    command: list[str], stdin: str | None = None, dry_run: bool = False
) -> subprocess.CompletedProcess[str]:
    """
    Run a subprocess command while logging its output in real-time.
    :param command: The command to run as a list of strings.
    :param stdin: Optional string to send to the command's stdin.
    :param dry_run: If True, log the command without executing it.
    :return: A CompletedProcess instance containing the command's results.
    """
    command = [str(arg) if isinstance(arg, Path) else arg for arg in command]
    command_string = shlex.join(command)
    command_name = command[0]

    if dry_run:
        logger.info(f"Dry run enabled, would have run command: {command_string}")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    logger.info(f"Running command: {command_string}")

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdin_pipe = cast("TextIO", process.stdin)
    if stdin is not None:
        stdin_pipe.write(stdin)
    stdin_pipe.close()

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    sel = selectors.DefaultSelector()
    sel.register(process.stdout, selectors.EVENT_READ, "stdout")
    sel.register(process.stderr, selectors.EVENT_READ, "stderr")

    while sel.get_map():
        for key, _ in sel.select():
            line = key.fileobj.readline()
            if not line:
                sel.unregister(key.fileobj)
                continue
            line = line.rstrip()
            if key.data == "stdout":
                stdout_lines.append(line)
                logger.debug(f"{command_name} stdout: {line}")
            else:
                stderr_lines.append(line)
                logger.debug(f"{command_name} stderr: {line}")

    process.wait()

    if process.returncode != 0:
        logger.warning(f"Command failed (exit {process.returncode})")

    logger.info(f"Command completed (exit {process.returncode})")
    return subprocess.CompletedProcess(
        args=command,
        returncode=process.returncode,
        stdout="\n".join(stdout_lines),
        stderr="\n".join(stderr_lines),
    )
