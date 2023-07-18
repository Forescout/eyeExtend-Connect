import logging
from typing import Any, Dict, List





def run() -> List[Dict[str, Any]]:
    user_params = xdome_works.parse_params(params)
    url = user_params["url"]
    token = user_params["token"]
    page_limit = int(user_params["max_devices_per_page"])
    total_limit = int(user_params["max_devices_limit"])

    filter_by = str(xdome_filter.build_query_filter(user_params["filter_params"]))

    logging.debug(f"URL: {url}, token: {token}, limit: {page_limit} filter: {filter_by}")
    devices_data = xdome_works.query_devices_from_xdome(
        url, token, page_limit, total_limit, filter_by, ssl_verify
    )
    return xdome_works.demux_multinic_devices(devices_data)


logging.debug("Start running the xDome plugin!! ")
response = {"endpoints": run()}
logging.debug(f"Finish running the xDome plugin : {response}")
