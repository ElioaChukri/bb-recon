from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class KatanaResult:
    """
    Data class to represent a katana result entry.
    """

    url: str
    method: str
    # If response is missing, these fields can be None
    status_code: int | None
    content_length: int | None
    content_type: str | None

    @classmethod
    def from_json_line(cls, line: str) -> KatanaResult:
        """
        Create a KatanaResult instance from a JSON line.

        :param line: str: A JSON-formatted string representing a katana result.
        :return: KatanaResult: The created instance.
        :raises json.JSONDecodeError: If the line is not valid JSON.
        :raises KeyError: If required keys are missing in the JSON data.
        """
        data: dict = json.loads(line)
        request_dict = data["request"]
        response = data.get("response") or {}
        status_code = response.get("status_code")
        content_length = response.get("content_length")
        content_type = response.get("headers", {}).get("Content-Type")
        return cls(
            url=request_dict["endpoint"],
            method=request_dict["method"],
            status_code=status_code,
            content_length=content_length,
            content_type=content_type,
        )

    @property
    def host(self) -> str:
        """
        Extract the host from the URL.

        :return: str: The host part of the URL.
        """

        parsed_url = urlparse(self.url)
        return parsed_url.netloc


def parse_katana_output(output: str) -> list[KatanaResult]:
    """
    Parse the output from katana and return a list of KatanaResult instances.

    :param output: str: The raw output from katana.
    :return: list[KatanaResult]: A list of parsed KatanaResult instances.
    """
    return [KatanaResult.from_json_line(line) for line in output.strip().splitlines() if line]
