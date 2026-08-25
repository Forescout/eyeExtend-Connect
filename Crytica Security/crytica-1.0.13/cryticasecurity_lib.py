# cryticasecurity_lib.py
#
# Shared helper code for the Crytica Connect App.
#
# IMPORTANT (Connect App constraint): library files are auto-imported by the
# Forescout framework and CANNOT access the pre-injected `params` or `response`
# globals. Any value a helper needs must be passed in as a function argument.
#
# This app is an INBOUND (push) integration: Crytica sends alert data to
# Forescout's Connect web API. Forescout does not call out to Crytica, so there
# is no outbound HTTP client, auth, polling, or resolve logic here. These
# helpers exist only to keep the test script small and to document the expected
# inbound payload shape for future maintainers.


# Every individual property the app expects in the inbound message's
# `properties` object. Each is a standalone scalar Forescout property (not a
# composite); a scalar resolve replaces the endpoint's current value, so each
# inbound POST overwrites the properties it carries. Do NOT add
# "overwrite": true to these in property.conf: the connect module registers
# any overwrite property as SIMPLE_LIST (before checking the scalar type) and
# the web API then rejects scalar values. Kept here so the test script (and
# any future script) can sanity-check an inbound payload against the declared
# schema without duplicating the list. These match the property tags in
# property.conf.
#
# The declared type matters as much as the name. Forescout stores a `date`
# property as epoch MILLISECONDS; hand it seconds and it is accepted without
# complaint and displays as a 1970 date, which looks like Crytica sent bad
# data rather than like a unit mismatch. That failure is silent everywhere
# except the console, so it is checked here.
PROPERTY_TYPES = {
    "connect_cryticasecurity_AlertTypeName": "string",
    "connect_cryticasecurity_AlertTypeDescription": "string",
    "connect_cryticasecurity_AlertCategoryName": "string",
    "connect_cryticasecurity_AlertCategoryDescription": "string",
    "connect_cryticasecurity_AlertSubcategoryName": "string",
    "connect_cryticasecurity_AlertSubcategoryDescription": "string",
    "connect_cryticasecurity_AlertEventTimestamp": "date",
    "connect_cryticasecurity_AlertMessage": "string",
    "connect_cryticasecurity_ScanDate": "date",
    "connect_cryticasecurity_ScannedElements": "integer",
    "connect_cryticasecurity_TotalElements": "integer",
    "connect_cryticasecurity_ScanScope": "string",
    "connect_cryticasecurity_ScanAlertsCounter": "integer",
    "connect_cryticasecurity_ElementName": "string",
    "connect_cryticasecurity_ElementCreateDate": "date",
    "connect_cryticasecurity_DeviceUid": "string",
    "connect_cryticasecurity_DeviceName": "string",
    "connect_cryticasecurity_DeviceOsTypeName": "string",
    "connect_cryticasecurity_DeviceOsFlavor": "string",
    "connect_cryticasecurity_DeviceOsDescription": "string",
    "connect_cryticasecurity_DeviceProcessorTypeName": "string",
}

# Derived rather than repeated, so the two cannot disagree.
ALERT_PROPERTIES = list(PROPERTY_TYPES)

# Below this, a value in a date property is far more likely to be seconds
# than milliseconds: as milliseconds it would be 1973, before which Crytica
# did not exist, and as seconds it is 2001 onwards. Anything genuinely older
# than 1973 is not a real scan timestamp either.
MIN_EPOCH_MILLIS = 100000000000


def _is_ip_address(value):
    """True for a well-formed IPv4 or IPv6 address.

    Hand-rolled rather than using ipaddress, because this module is imported
    by the Forescout framework into an embedded interpreter whose standard
    library is not guaranteed to match a desktop Python. The check only has
    to separate an address from a hostname or a typo, which this does.
    """
    if not isinstance(value, str):
        return False
    text = value.strip()
    if ":" in text:
        # IPv6. Enough structure to reject a hostname without reimplementing
        # the grammar: hex groups, at most one "::", and a plausible count.
        if text.count("::") > 1:
            return False
        groups = [g for g in text.replace("::", ":").split(":") if g != ""]
        if not groups or len(groups) > 8:
            return False
        for group in groups:
            if len(group) > 4:
                return False
            try:
                int(group, 16)
            except ValueError:
                return False
        return True

    octets = text.split(".")
    if len(octets) != 4:
        return False
    for octet in octets:
        if not octet.isdigit() or (len(octet) > 1 and octet[0] == "0"):
            return False
        if int(octet) > 255:
            return False
    return True


# IMPORTANT (Connect App constraint): the framework's Python sandbox blocks
# dunder attribute access, so reading a type's dunder name attribute raises
# inside the app even though it works in a plain interpreter. The token is
# kept out of this file entirely, comments included, because it is unclear
# whether the framework screens source text or only the parsed AST. The names
# are spelled out below instead, picked with isinstance. bool is checked
# before int because bool is a subclass of int and would otherwise report as
# "int" in the very message that exists to explain a bool was rejected.
_TYPE_NAMES = (
    (bool, "bool"),
    (int, "int"),
    (float, "float"),
    (str, "str"),
    (list, "list"),
    (dict, "dict"),
)


def _type_name(value):
    """Name the type of `value` without touching dunder attributes."""
    for py_type, name in _TYPE_NAMES:
        if isinstance(value, py_type):
            return name
    return "an unrecognised type"


def _check_types(props, keys):
    """Check declared types for the properties we recognise.

    Only known keys are checked. An unrecognised key has no declared type, and
    guessing one would turn "Crytica added a field" into a rejected payload.

    Returns (ok, reason). Booleans are rejected for integer and date
    properties on purpose: bool is a subclass of int in Python, so True would
    otherwise sail through and resolve as 1.
    """
    for key in sorted(keys):
        expected = PROPERTY_TYPES.get(key)
        if expected is None:
            continue
        value = props[key]
        if value is None:
            continue

        if expected == "string":
            if not isinstance(value, str):
                return False, (
                    "Property '{}' is declared string but carries {}.".format(
                        key, _type_name(value))
                )
            continue

        if isinstance(value, bool) or not isinstance(value, int):
            return False, (
                "Property '{}' is declared {} but carries {}. Forescout will "
                "reject or mis-store a value of the wrong type.".format(
                    key, expected, _type_name(value))
            )

        if expected == "date" and 0 < value < MIN_EPOCH_MILLIS:
            return False, (
                "Property '{}' looks like epoch SECONDS ({}). Forescout date "
                "properties are epoch milliseconds; sending seconds is accepted "
                "silently and displays as a 1970 date. Multiply by 1000.".format(
                    key, value)
            )

    return True, ""


def validate_inbound_payload(payload):
    """Validate the shape of a single inbound Crytica web-API message.

    Expected structure (the Connect web-API inbound format):
        {
          "ip": "10.110.1.157",
          "properties": {
            "connect_cryticasecurity_AlertId": "2.2.4.a",
            "connect_cryticasecurity_AlertTypeDescription": "An executable element was added to the protected device",
            ...one key per individual property...
          }
        }

    Args:
        payload: dict parsed from the inbound JSON body.

    Returns:
        (ok, message) tuple. `ok` is True when the payload has a usable
        endpoint identifier and a well-formed properties object; otherwise
        False with a human-readable reason. Unknown property keys are reported
        but do NOT fail validation, since Crytica may add fields over time.
    """
    if not isinstance(payload, dict):
        return False, "Payload is not a JSON object."

    if not payload.get("ip"):
        return False, "Payload is missing the 'ip' endpoint identifier."

    if not _is_ip_address(payload["ip"]):
        return False, (
            "Payload 'ip' is '{}', which is not an IP address. The Connect web "
            "API keys each message to an endpoint by address, so a hostname or "
            "a malformed address resolves against nothing and the alert is "
            "dropped without an error.".format(payload["ip"])
        )

    props = payload.get("properties")
    if not isinstance(props, dict):
        return False, "Payload is missing the 'properties' object."

    known = set(ALERT_PROPERTIES)
    app_keys = {k for k in props.keys() if k.startswith("connect_cryticasecurity_")}
    if not app_keys:
        return False, "Payload carries no connect_cryticasecurity_* properties."

    for key in app_keys:
        if isinstance(props[key], (dict, list)):
            return False, "Property '{}' must be a scalar value, not an object or list.".format(key)

    ok, reason = _check_types(props, app_keys)
    if not ok:
        return False, reason

    unknown = app_keys - known
    if unknown:
        return True, "Payload is valid. Note: unrecognized propert{} present and ignored: {}".format(
            "y" if len(unknown) == 1 else "ies", ", ".join(sorted(unknown))
        )

    return True, "Payload is valid ({} Crytica propert{}).".format(
        len(app_keys), "y" if len(app_keys) == 1 else "ies"
    )
