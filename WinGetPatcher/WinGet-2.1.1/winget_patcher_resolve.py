# ============================================================
#  WinGet Patcher - Property Resolver Script
#  Version: 0.4.4 (consolidated subfields: count + apps multi-line)
# ============================================================
#
#  CHANGE FROM 0.4.2:
#  - Composite property now has TWO subfields instead of three:
#    * wingetpatcher_updates_count (int)
#    * wingetpatcher_updates_apps  (multi-line string, one app per line)
#  - The old wingetpatcher_updates_list and wingetpatcher_updates_detail
#    subfields are removed. Their content is merged into wingetpatcher_
#    updates_apps in the format "PackageId (current -> available)".
#  - Substring matching ("contains 'Google.Chrome'") still works because
#    every line contains the full package ID.
#  - Fixed a latent bug: previous version used `if parsed.get('count'):`
#    which would silently drop a legitimate count of 0. Changed to
#    `is not None` so 0-count endpoints still get the property set.
#
#  CHANGE FROM 0.4.1 (v0.4.2, Cole Wilson):
#  Library functions must be called via the module namespace:
#  winget_patcher_lib.parse_winget_output(...). Defensive dict access
#  with .get() prevents KeyError crashes that would silently kill the
#  resolver mid-execution.
#
#  CHANGE FROM 0.3.0 (v0.4.1):
#  Added explicit `import logging` and `import json` at the top.
#  The framework does not auto-inject these standard library modules.
#
# ============================================================
import logging
import json
# ============================================================
#
#  This script is invoked by the Forescout Connect framework when
#  the WinGet Patcher composite property needs to be resolved
#  for an endpoint:
#    - connect_wingetpatcher_updates_info  (composite, with subfields:
#        wingetpatcher_updates_count,
#        wingetpatcher_updates_apps)
#
#  The script reads the captured output of WingetDiscover_v3.ps1
#  from the `params` dict, parses the two structured output
#  lines, and returns property values via the `response` dict.
#
#  ARCHITECTURE NOTE:
#  This script depends on the HPS-captured script result being
#  available at params['script_result.<HASH>'], where <HASH> is
#  the Forescout-assigned identifier for the discovery script.
#  The hash must match the dependency declared in property.json
#  and the FIELD_NAME in the policy template XML. All two must
#  carry the same hash for the wiring to work.
#
#  This mechanism is not documented in Forescout's official
#  Connect App Building Guide. It is used in production by the
#  C2C Reporting Connect app (Cole Wilson, Forescout DoD).
#
#  COMPOSITE PROPERTY PATTERN:
#  This version uses Cole's exact pattern from C2C: ONE composite
#  property with subfields. The resolver returns a dict for the
#  composite property's tag, with subfield tags as keys.
#
#  This pattern is required - prior version (0.2.x) used three
#  separate resolvable properties pointing to the same resolver,
#  which registers cleanly but the framework never invokes the
#  resolver. The composite pattern matches C2C exactly and is
#  proven to work.
#
#  SANDBOX CONSTRAINTS:
#  Connect Python is heavily sandboxed. The following imports
#  are BANNED: os, subprocess, open, print, io, pathlib,
#  importlib, sys, threading. The framework injects `params`
#  (input dict) and `response` (output dict) as globals. For
#  the standard library, we import explicitly (see top of file)
#  to match Cole's C2C resolver pattern.
#
#  LIBRARY FILE NOTE:
#  parse_winget_output() and WINGET_NOT_FOUND_SENTINEL are
#  defined in winget_patcher_lib.py, which the framework loads
#  automatically as an importable module. Reference them via
#  the module namespace: winget_patcher_lib.parse_winget_output(...)
#  Do NOT add an `import winget_patcher_lib` line at the top -
#  the framework has already loaded the module, you just need
#  to use its name when calling its members.
#
# ============================================================

# -- CONFIGURATION --
# This is the script_result hash for WingetDiscover_v3.ps1.
# It must match (a) the dependency declared in property.json
# and (b) the FIELD_NAME in the discovery policy template XML.


DISCOVERY_SCRIPT_RESULT_KEY = "script_result.836bc66aeb43db5a544233dec55a1f0b"


# ============================================================
#  MAIN RESOLVER LOGIC
# ============================================================
#
# Framework convention: the resolver runs as a script body (not a
# function call). The framework provides `params` (input dict) and
# we populate `response` (output dict).
#
# For composite properties, the response structure is:
#   response['properties'] = {
#     'connect_wingetpatcher_updates_info': {
#       'wingetpatcher_updates_count': <int>,
#       'wingetpatcher_updates_apps': <str>
#     }
#   }

response = {}
properties = {}
updates_info = {}

logging.debug("WinGetPatcher resolver invoked.")

# Step 1: Look up the captured HPS script output.
raw_output = params.get(DISCOVERY_SCRIPT_RESULT_KEY)

if not raw_output:
    # The discovery script hasn't run on this endpoint yet, or its
    # result has expired from the Forescout cache. This is not an
    # error - it just means the property will be marked unresolved,
    # which is the correct state. The discovery policy will populate
    # it on its next run.
    logging.debug(
        "WinGetPatcher resolver: no script_result available for {}. "
        "Property will remain unresolved until discovery runs.".format(
            DISCOVERY_SCRIPT_RESULT_KEY
        )
    )
    response["properties"] = properties

else:
    # Step 2: Parse the structured output. parse_winget_output is
    # defined in winget_patcher_lib.py - access via module namespace.
    parsed = winget_patcher_lib.parse_winget_output(raw_output)
    logging.debug(
        "WinGetPatcher resolver parsed: count={}, apps_len={}".format(
            parsed.get("count"),
            len(parsed["apps"]) if parsed.get("apps") is not None else None,
        )
    )

    # Step 3: Populate subfields. If any individual field was malformed
    # or absent, we skip that subfield rather than corrupting it.
    # NOTE: parsed.get('count') == 0 is FALSY but valid - use 'is not None'.

    if parsed.get("count") is not None:
        updates_info["wingetpatcher_updates_count"] = parsed["count"]

    if parsed.get("apps") is not None:
        updates_info["wingetpatcher_updates_apps"] = parsed["apps"]

    # Only set the composite property if we got at least one subfield.
    if updates_info:
        properties["connect_wingetpatcher_updates_info"] = updates_info

    response["properties"] = properties

logging.debug(
    "WinGetPatcher resolver done. Returned: {}".format(properties)
)
# The framework reads `response` after the script body finishes.
# print(json.dumps(response))  # For debugging - can be removed in production
