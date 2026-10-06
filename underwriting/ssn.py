"""Pull the SSN out of a submission. That value is the case id and bureau key."""

from __future__ import annotations

import re
from typing import Optional

_SSN = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")


def extract_ssn(text: str) -> Optional[str]:
    """Return the first SSN in the text, formatted as AAA-GG-SSSS."""
    if not text:
        return None
    match = _SSN.search(text)
    if match is None:
        return None
    area, group, serial = match.groups()
    if area == "000" or group == "00" or serial == "0000":
        return None
    return "{0}-{1}-{2}".format(area, group, serial)
