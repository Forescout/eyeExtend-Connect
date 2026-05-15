# ============================================================
#  WinGet Patcher - Shared Library
#  Version: 0.4.4 (parse_winget_output rewritten for multi-line
#  WINGET_UPDATES_APPS field; consolidated from 3 fields to 2)
# ============================================================
#
#  This file is registered in property.json with "library_file": true.
#  The Connect framework loads it at app import time as a Python
#  module. Other scripts reference its members via the module name
#  (e.g. winget_patcher_lib.parse_winget_output(...)).
#
#  Note on Forescout's App Building Guide documentation:
#  > Scripts that use library files defined in the property.conf file
#  > must not include the import statement that refers to these library
#  > files because they have already been dynamically loaded when the
#  > app was imported.
#
#  The guide is correct that you don't write 'import winget_patcher_lib'
#  - the framework has already loaded the module. But you DO call its
#  members via the module name, not as if they were globals.
#
# ============================================================

# Version of the WinGet Patcher Connect app library.
__version__ = "0.4.4"

# Sentinel value emitted by WingetDiscover.ps1 in the COUNT field
# when winget.exe cannot be located on the endpoint.
WINGET_NOT_FOUND_SENTINEL = -1

# Field markers we recognize in the discovery script's output. Any line
# starting with one of these is treated as the start of a new field.
# Used by parse_winget_output() to know where a multi-line field ends.
_DISCOVERY_FIELD_MARKERS = (
    "WINGET_UPDATES_COUNT=",
    "WINGET_UPDATES_APPS=",
)


def parse_winget_output(raw):
    """Parse the structured output emitted by WingetDiscover.ps1.

    The discovery script emits two named fields:

        WINGET_UPDATES_COUNT=<integer>
        WINGET_UPDATES_APPS=<line 1>
        <line 2>
        <line 3>
        ...

    WINGET_UPDATES_APPS is multi-line: each line after the marker is
    one "PackageId (current -> available)" entry, until end-of-input
    or another WINGET_UPDATES_* marker line. This parser handles that
    properly, unlike a simple line-by-line scan.

    Args:
        raw: The raw text output captured from the HPS script execution.
             May contain other lines (PowerShell errors, etc.) before
             the first WINGET_UPDATES_* marker, which we ignore.

    Returns:
        A dict with two keys:
            count - int or None (None if the line was absent;
                    WINGET_NOT_FOUND_SENTINEL if winget could not run)
            apps  - str or None (multi-line "id (cur -> avail)" entries,
                    one per line, OR a single sentinel string like
                    "ERROR_WINGET_NOT_FOUND" if discovery failed)
    """
    parsed = {"count": None, "apps": None}

    if not raw:
        return parsed

    # Normalize line endings - Windows scripts emit CRLF; Forescout
    # may or may not normalize, so we handle both.
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("WINGET_UPDATES_COUNT="):
            value = line.split("=", 1)[1].strip()
            try:
                parsed["count"] = int(value)
            except (ValueError, TypeError):
                # Malformed count line - signal "winget not functional"
                # rather than crashing the resolver.
                parsed["count"] = WINGET_NOT_FOUND_SENTINEL
            i += 1

        elif line.startswith("WINGET_UPDATES_APPS="):
            # First line of the APPS field: everything after the '='.
            apps_lines = [line.split("=", 1)[1]]
            i += 1
            # Continue collecting lines until we hit another marker
            # or run out of input.
            while i < len(lines):
                next_line = lines[i]
                if any(next_line.startswith(m) for m in _DISCOVERY_FIELD_MARKERS):
                    break
                apps_lines.append(next_line)
                i += 1
            # Strip trailing empty lines but preserve internal blank lines
            # (unlikely in practice but defensive).
            while apps_lines and apps_lines[-1].strip() == "":
                apps_lines.pop()
            parsed["apps"] = "\n".join(apps_lines)

        else:
            i += 1

    return parsed
