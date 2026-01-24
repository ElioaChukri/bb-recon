from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum


class DnsStatusCode(StrEnum):
    NOERROR = "NOERROR"
    FORMERR = "FORMERR"
    SERVFAIL = "SERVFAIL"
    NXDOMAIN = "NXDOMAIN"
    NOTIMP = "NOTIMP"
    REFUSED = "REFUSED"
    YXDOMAIN = "YXDOMAIN"
    XRRSET = "XRRSET"
    NOTAUTH = "NOTAUTH"
    NOTZONE = "NOTZONE"


@dataclass(frozen=True)
class DnsxResult:
    host: str
    resolver: tuple[str]
    a_record: tuple[str]
    status_code: DnsStatusCode

    @classmethod
    def from_json_line(cls, line: str) -> DnsxResult:
        """
        Create a DnsxResult instance from a JSON line.
        :param line: str: A JSON-formatted string representing a dnsx result.
        :return: DnsxResult: The created instance.
        :raises json.JSONDecodeError: If the line is not valid JSON.
        :raises KeyError: If required keys are missing in the JSON data.
        """
        data = json.loads(line)
        return cls(
            host=data["host"],
            resolver=tuple(data.get("resolver", [])),
            a_record=tuple(data.get("a", [])),
            status_code=DnsStatusCode(data["status_code"]),
        )


def parse_dnsx_output(output: str) -> list[DnsxResult]:
    """
    Parse the output from dnsx and return a list of DnsxResult instances.

    :param output: str: The raw output from dnsx.
    :return: list[DnsxResult]: A list of parsed DnsxResult instances.
    """
    return [DnsxResult.from_json_line(line) for line in output.strip().splitlines() if line]
