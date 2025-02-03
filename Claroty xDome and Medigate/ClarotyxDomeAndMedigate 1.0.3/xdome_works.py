import json
import logging
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import requests  # type: ignore[import]



PARAMS_PREFIX = "connect_clarotyxdomeandmedigate_"

MAPPING_XDOME_TO_FS_FIELDS = {
    "ip_list": "ip",
    "mac_list": "mac",
    "manufacturer": "manufacturer",
    "device_type": "device_type",
    "model": "model",
    "device_category": "device_category",
    "device_subcategory": "device_subcategory",
    "uid": "uid",
    "site_name": "site_name",
    "authentication_user_list": "authentication_user",
    "enforcement_or_authorization_profiles_list": "enforcement_or_auth_profiles",
    "labels": "labels",
    "combined_os": "os",
    "first_seen_list": "first_seen",
    "last_seen_list": "last_seen",
    "risk_score": "risk_score",
    "equipment_class": "equipment_class",
    "switch_location_list": "switch_location",
    "ap_location_list": "ap_location",
    "ssid_list": "ssid",
    "switch_name_list": "switch_name",
    "ip_assignment_list": "ip_assignment",
    "connection_type_list": "connection_type",
    "switch_port_list": "switch_port_id",
    "http_hostnames": "http_hostnames",
    "snmp_hostnames": "snmp_hostnames",
    "is_online": "status",
    "number_of_nics": None,
}

FIELDS_TO_DEMUX = {
    "ip_list",
    "mac_list",
    "first_seen_list",
    "last_seen_list",
    "switch_location_list",
    "ap_location_list",
    "ssid_list",
    "ip_assignment_list",
    "connection_type_list",
    "switch_port_list",
    "authentication_user_list",
    "enforcement_or_authorization_profiles_list",
    "switch_name_list",
}


def extract_ip_address(ip_string: Optional[str] = None) -> Optional[str]:
    if not ip_string:
        return None
    pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"  # Regular expression pattern for IP address
    match = re.search(pattern, ip_string)
    if match:
        ip_address = match.group()
        return ip_address
    else:
        return None


def extract_mac_address(mac: str) -> str:
    return mac.replace(":", "")


def timestamp_to_epoch_seconds(timestamp_string: str) -> int:
    format_str = (
        "%Y-%m-%dT%H:%M:%S%z" if timestamp_string.rfind(".") == -1 else "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    # Python 3.6 does not support %z with ':' , so we need to remove the colon from the timezone
    timestamp_string = (
        timestamp_string[:-3] + timestamp_string[-2:]
        if timestamp_string[-3] == ":"
        else timestamp_string
    )
    dt = datetime.strptime(timestamp_string, format_str)

    epoch_seconds = int(dt.timestamp())
    return epoch_seconds


values_parsing_callback: Dict[str, Callable[..., Any]] = {
    "ip": extract_ip_address,
    "mac": extract_mac_address,
    f"{PARAMS_PREFIX}first_seen": timestamp_to_epoch_seconds,
    f"{PARAMS_PREFIX}last_seen": timestamp_to_epoch_seconds,
}


def process_value(key: str, value: str) -> Tuple[str, Optional[Union[str, List[str]]]]:
    if key == "ip_list":
        new_key = "ip"
    elif key == "mac_list":
        new_key = "mac"
    else:
        new_key = f"{PARAMS_PREFIX}{MAPPING_XDOME_TO_FS_FIELDS[key]}"
    if value is None or value == "None" or (isinstance(value, list) and len(value) == 0):
        return new_key, None

    if new_key in values_parsing_callback:
        value = values_parsing_callback[new_key](value)

    return new_key, value


def demux_multinic_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    demuxed_devices = []

    for device_info in devices:
        try:
            number_of_nics = device_info["number_of_nics"]
            base_device_info = {}
            for field_name in MAPPING_XDOME_TO_FS_FIELDS.keys() - FIELDS_TO_DEMUX:
                if (
                    MAPPING_XDOME_TO_FS_FIELDS[field_name] is not None
                    and field_name in device_info
                ):
                    key, value = process_value(field_name, device_info[field_name])
                    if value is not None:
                        base_device_info[key] = value

            if number_of_nics > 0:
                for idx in range(number_of_nics):
                    demuxed_device_properties = base_device_info.copy()
                    for field_name in FIELDS_TO_DEMUX:
                        if field_name in device_info:
                            key, value = process_value(field_name, device_info[field_name][idx])
                            if value is not None:
                                demuxed_device_properties[key] = value
                    if "mac" not in demuxed_device_properties:
                        continue
                    ip = demuxed_device_properties.pop("ip", None)
                    mac = demuxed_device_properties.pop("mac", None)
                    host: Dict[str, Any] = {}
                    if ip is not None:
                        host["ip"] = ip
                    if mac is not None:
                        host["mac"] = mac
                    host["properties"] = demuxed_device_properties

                    demuxed_devices.append(host)
        except Exception as e:
            logging.error(f"Failed to demux device {device_info}, error: {e}")

    return demuxed_devices


def make_api_post_request(
    url: str, token: str, data: Dict[str, Any], ssl_verify_val: Union[bool, str] = False
) -> Tuple[int, Union[Dict[str, Any], str]]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, json=data, verify=ssl_verify_val)

    if resp.status_code == 200:
        logging.debug("HTTP POST request successful")
        return resp.status_code, resp.json()
    else:
        logging.error(
            f"HTTP POST request failed with status code: "
            f"{resp.status_code} and response: {resp.content!r}"
        )
    return resp.status_code, resp.content.decode("utf-8")


def query_devices_from_xdome(
    url: str,
    token: str,
    page_limit: int,
    total_limit: int,
    filter_val: Optional[str] = None,
    ssl_verify_val: Union[bool, str] = False,
) -> List[Dict[str, Any]]:
    result = []
    offset: int = 0
    while int(offset) < int(total_limit):
        remaining_entries_count = total_limit - offset
        next_page_limit = min(page_limit, remaining_entries_count)
        data = {
            "offset": offset,
            "limit": next_page_limit,
            "fields": list(MAPPING_XDOME_TO_FS_FIELDS.keys()),
            "include_count": True,
        }
        if filter_val is not None:
            data["filter_by"] = json.loads(filter_val)
        logging.debug(
            f"Making request with offset: {offset}, limit: {next_page_limit}, "
            f"remaining_entries_count: {remaining_entries_count} "
        )
        status_code, http_resp = make_api_post_request(url, token, data, ssl_verify_val)
        if status_code != 200 or not isinstance(http_resp, dict):
            logging.error(f"Failed to get data from the xDome API: {http_resp}")
            break

        devices_data = http_resp["devices"]
        if devices_data is None:
            logging.warning("No devices returned from the xDome API")
            continue

        current_devices_count = len(devices_data)
        logging.debug(f"Got {current_devices_count} devices from the xDome API")
        offset += current_devices_count
        result.extend(devices_data)
        logging.debug(
            f"done request with offset: {offset}, limit: {page_limit}, "
            f"current_devices_count:{current_devices_count}"
        )
        if current_devices_count < page_limit:
            break

    return result


def parse_params(user_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if user_params is None:
        user_params = params
    parsed_params = {}
    filter_params = {}
    filter_prefix = "filter_"
    for key, value in user_params.items():
        key = key[len(PARAMS_PREFIX) :] if key.startswith(PARAMS_PREFIX) else key
        if filter_prefix in key:
            filter_key = key[len(filter_prefix) :] if key.startswith(filter_prefix) else key
            filter_params[filter_key] = value
        else:
            parsed_params[key] = value

    parsed_params["filter_params"] = filter_params

    return parsed_params
