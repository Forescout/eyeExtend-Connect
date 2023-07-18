import json
import logging
from typing import Any, Dict, Tuple, Union


user_params = xdome_works.parse_params(params)


def run() -> Tuple[int, Union[Dict[str, Any], str]]:
    logging.debug(f" testparams: {user_params} ssl-verify: {ssl_verify} ")
    url = user_params["url"]
    token = user_params["token"]
    logging.debug(f"filter params : {user_params}")
    try:
        filter_val = str(xdome_filter.build_query_filter(user_params["filter_params"]))
    except Exception as e:
        logging.debug(f"Exception while building filter : {e}")
        return -1, str(e)
    logging.debug(f"filter_val : {filter_val}")
    data = {
        "offset": 0,
        "limit": 1,
        "fields": list(xdome_works.MAPPING_XDOME_TO_FS_FIELDS.keys()),
        "include_count": True,
    }
    if filter_val:
        data["filter_by"] = json.loads(filter_val)
    return xdome_works.make_api_post_request(url, token, data, ssl_verify)


logging.debug("Start running the xDome plugin test")
response: Dict[str, Any] = {}

status_code, msg = run()
if status_code == 200:
    response["succeeded"] = True
    if isinstance(msg, dict):
        count = msg.get("count")
        if count is None:
            device_count = 0
        else:
            device_count = int(count)
    else:
        device_count = 0
    warning_msg = ""
    device_limit_count = user_params.get("device_limit_count", 100000)
    if device_count > device_limit_count:
        warning_msg = (
            f"\nWarning: The number of devices discovered ({device_count}) exceeds the limit "
            f"set in the configuration ({device_limit_count})."
        )
    response[
        "result_msg"
    ] = f"Test Successful! Total Connected Devices: {device_count}.\n{warning_msg}"
else:
    response["succeeded"] = False
    response["result_msg"] = f"Could not connect to xDome server : {msg}"

logging.debug(
    f"Finish running the xDome plugin test with response :status_code: {status_code}, msg: {msg}"
)
