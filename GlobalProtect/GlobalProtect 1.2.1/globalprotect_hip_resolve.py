"""
Copyright © 2021 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to  permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging

logging.debug("Resolve for GlobalProtect HIP Report")

# Params needed for resolve
connection = globalprotect_library.Connection()
connection.server = params.get("connect_globalprotect_server")
connection.username = params.get("connect_globalprotect_admin_username")
connection.password = params.get("connect_globalprotect_admin_password")
connection.use_syslog = params.get("connect_globalprotect_use_syslog")
connection.server_from_syslog = params.get("connect_globalprotect_firewall")
connection.ssl_context = ssl_context
ip = params.get("ip")


def get_user_hip_report(info_user):
    """
    Call API to get user hip report
    Extract information from APIResponse to get data of anti-malware, disk-backup, disk-encryption, firewall, patch-management & missing-patches
    Initialize and Update GPHipReport object gp_hip_report to store the information
    """
    logging.debug("In get_user_hip_report")
    api_resp_user_info = connect_gp.call_api("OC_SHOW_HIP_REPORT", info_user)
    # result should be a APIResponse
    if api_resp_user_info.is_successful:
        # <response status="success">
        # <result>
        # <hip-report>
        # <categories>
        # <entry name="anti-malware">
        # <...>
        # </entry>
        # <entry name="disk-backup">
        # <...>
        # </entry>
        # <entry name="disk-encryption">
        # <...>
        # </entry>
        # <entry name="firewall">
        # <...>
        # </entry>
        # <entry name="patch-management">
        # <...>
        # </entry>
        # </categories>
        # </hip-report>
        # </result>
        # </response>
        result_tree = api_resp_user_info.xml_content
        hip_report = result_tree.find('hip-report/categories')
        categories = ['anti-malware', 'disk-backup', 'disk-encryption', 'firewall', 'patch-management']
        gp_hip_report = globalprotect_library.GPHipReport()
        for category in categories:
            hip_per_category_list = hip_report.find('entry[@name="'+category+'"]/list')
            if category == 'anti-malware':
                gp_hip_report.anti_malware = globalprotect_library.get_hip_anti_malware_info(hip_per_category_list)
            elif category == 'disk-backup':
                gp_hip_report.disk_backup = globalprotect_library.get_hip_disk_backup_info(hip_per_category_list)
            elif category == 'disk-encryption':
                gp_hip_report.disk_encryption = globalprotect_library.get_hip_disk_encryption_info(hip_per_category_list)
            elif category == 'firewall':
                gp_hip_report.firewall = globalprotect_library.get_hip_firewall_info(hip_per_category_list)
            elif category == 'patch-management':
                gp_hip_report.patch_mgmt = globalprotect_library.get_hip_patch_management_info(hip_per_category_list)
        # get missing patches info, "missing-patches" tag is child of "patch-management"
        hip_mp_list = hip_report.findall('entry[@name="patch-management"]/missing-patches/entry')
        gp_hip_report.missing_patches = globalprotect_library.get_hip_missing_patches_info(hip_mp_list)
        return gp_hip_report
    else:
        return None

# Init GP class
logging.debug("Init library")
connect_gp = globalprotect_library.FSConnectGP()
connect_gp.set_init(connection)

# Get the key_token first. All other API calls require this.
token = connect_gp.token.token
token_error = connect_gp.token.error_msg

# Return objects
response = {}
properties = {}

# Token is invalid
if token is None:
    error_msg = globalprotect_library.FSConnectGP.get_error_msg("Failed to get token.", token_error)
    response["succeeded"] = False
    # For resolve, put in error
    response["error"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Call user IP mapping")
    # Get user
    ip_user, ip_type, virtual_sys = globalprotect_library.get_ip_user_mapping(connect_gp, ip)
    logging.debug("Full User: {}".format(ip_user))
    logging.debug("IP type: {}".format(ip_type))
    logging.debug("Virtual system: {}".format(virtual_sys))
    error_msg = ""

    if ip_user:
        user_no_domain = globalprotect_library.parse_ip_user(ip_user)
        gp_info_list = globalprotect_library.get_user_gateway_info(connect_gp, user_no_domain)
        # Hash is not null and has values
        if gp_info_list and ip in gp_info_list:
            gp_info = gp_info_list[ip]
            info_user = {
                "computer": gp_info.computer,
                "ip": ip,
                "user": ip_user
            }
            logging.debug("Info User: {}".format(info_user))
            gp_hip_report = get_user_hip_report(info_user)
            properties["connect_globalprotect_HIP_anti_malware"] = gp_hip_report.anti_malware
            properties["connect_globalprotect_HIP_disk_backup"] = gp_hip_report.disk_backup
            properties["connect_globalprotect_HIP_disk_encryption"] = gp_hip_report.disk_encryption
            properties["connect_globalprotect_HIP_firewall"] = gp_hip_report.firewall
            properties["connect_globalprotect_HIP_patch_mgmt"] = gp_hip_report.patch_mgmt
            properties["connect_globalprotect_HIP_missing_patches"] = gp_hip_report.missing_patches
        else:
            error_msg += "No user gateway info found. "
    else:
        error_msg += "No user mapping info found. "

    # Store info
    response["properties"] = properties

    if len(error_msg) > 0:
        logging.error(error_msg)
        response["error"] = error_msg + "User might be disconnected."
