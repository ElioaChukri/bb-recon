from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class SubfinderResult:
    """
    Data class to represent a subfinder result entry.
    """

    host: str
    input: str
    sources: tuple[str, ...]

    @classmethod
    def from_json_line(cls, line: str) -> SubfinderResult:
        """
        Create a SubfinderResult instance from a JSON line.

        :param line: str: A JSON-formatted string representing a subfinder result.
        :return: SubfinderResult: The created instance.
        :raises json.JSONDecodeError: If the line is not valid JSON.
        :raises KeyError: If required keys are missing in the JSON data.
        """
        data = json.loads(line)
        return cls(host=data["host"], input=data["input"], sources=tuple(data.get("sources", [])))


def parse_subfinder_output(output: str) -> list[SubfinderResult]:
    """
    Parse the output from subfinder and return a list of SubfinderResult instances.

    :param output: str: The raw output from subfinder.
    :return: list[SubfinderResult]: A list of parsed SubfinderResult instances.
    """
    return [SubfinderResult.from_json_line(line) for line in output.strip().splitlines() if line]
