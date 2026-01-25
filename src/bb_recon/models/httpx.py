from __future__ import annotations

import json
import re
from dataclasses import dataclass

PROTOCOL_REGEX = re.compile(r"^https?://")


@dataclass(frozen=True)
class HttpxResult:
    """
    Data class to represent an httpx result entry.
    """

    url: str
    host: str
    port: int
    status_code: int
    content_length: int
    content_type: str
    title: str
    webserver: str

    @classmethod
    def from_json_line(cls, line: str) -> HttpxResult:
        """
        Create an HttpxResult instance from a JSON line.

        :param line: str: A JSON-formatted string representing an httpx result.
        :return: HttpxResult: The created instance.
        :raises json.JSONDecodeError: If the line is not valid JSON.
        :raises KeyError: If required keys are missing in the JSON data.
        """
        data: dict = json.loads(line)
        return cls(
            url=data["url"],
            host=PROTOCOL_REGEX.sub("", data["url"]),
            port=data["port"],
            status_code=data["status_code"],
            content_length=data["content_length"],
            content_type=data.get("content_type", ""),
            title=data.get("title", ""),
            webserver=data.get("webserver"),
        )


def parse_httpx_output(output: str) -> list[HttpxResult]:
    """
    Parse the output from httpx and return a list of HttpxResult instances.

    :param output: str: The raw output from httpx.
    :return: list[HttpxResult]: A list of parsed HttpxResult instances.
    """
    return [HttpxResult.from_json_line(line) for line in output.strip().splitlines() if line]
