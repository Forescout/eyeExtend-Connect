"""

Copyright © 2024 Absolute Software Corporation.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHE
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from datetime import datetime, timezone
import hashlib
import json
import time
import urllib.request
import jwt
import hmac
import logging
import re

'''
Absolute API 3.0 implementation
'''
# FIELD / SUBFIELD NAMES
ABSOLUTE_ID = "deviceUid"
ADAPTER_TYPE = 'adapterType'
AGENT_INSTALLED = 'agentInstalled'
AGENT_VERSION = 'agentVersion'
AGENT_STATUS = 'agentStatus'
ALL_DRIVES_ENCRYPTED = 'allDrivesEncrypted'
AVP_INFO = 'avpInfo'
AVP_STATUS = 'avpStatus'
AVP_NAME = 'antivirusName'
AVP_VERSION = 'antivirusVersion'
DEVICE_UID = 'deviceUid'
DEVICE_NAME = 'deviceName'
ESP_INFO = 'espInfo'
ESP_STATUS = 'encryptionStatus'
ESP_NAME = 'encryptionProductName'
ESP_VERSION = 'encryptionVersion'
HOURS_IN_LOCATION = 'hoursInLocation'
IS_IN_ITAR = 'isInItar'
GEO_DATA = 'geoData'
LOCATION = 'location'
GEO_ADDRESS = 'geoAddress'
CITY = 'city'
COUNTRY = 'country'
COUNTRY_CODE = 'countryCode'
INSTALLED = 'installed'
IPV4_ADDRESS = 'ipV4Address'
LAST_CONNECTED_DATETIME_UTC = "lastConnectedDateTimeUtc"
LAST_CONNECTED_DATETIME_EPOCH = "lastConnectedDateTimeEpoch"
LAST_LOCATION_UPDATE_DATETIME_UTC = 'lastLocationUpdateDateTimeUtc'
LAST_LOCATION_UPDATE_DATETIME_EPOCH = 'lastLocationUpdateDateTimeEpoch'

LAST_UPDATE_DATETIME_UTC = 'lastUpdateDateTimeUtc'
DAYS_OFFLINE = "hoursOffline"
LOCAL_IP = "localIp"
LOCATION_COUNTRY = 'locationCountry'
LOCATION_COUNTRY_CODE = 'locationCountryCode'
LOCATION_CITY = 'locationCity'
MAC = 'mac'
MAC_ADDRESS = 'macAddress'
MAC_ADDRESSES = 'macAddresses'
NAME = 'name'
PUBLIC_IP = "publicIp"
POLICY_GROUP_NAME = 'policyGroupName'
USERNAME = 'username'
NETWORK_ADAPTERS = 'networkAdapters'
NETWORK_ADAPTERS_MAC_ADDRESS = 'networkAdapters.macAddress'
OPERATING_SYSTEM = 'operatingSystem'
VERSION = 'version'
OS_VERSION = 'osVersion'
OS_NAME = 'osName'
STATUS = 'status'
STATUS_DETAILS = 'statusDetails'
DHCP_SERVER = 'dhcpServer'
DNS_HOSTNAME = 'dnsHostName'
PUBLIC_ADDRESS = 'publicIpAddress'

COMPLIANT_APP = 'compliantApp'
NO_DATA = 'No Data'
NOT_APPLICABLE = 'Not Applicable'
UNKNOWN = 'Unknown'

RNR_ANYCONNECT = "rnrANYCONNECT"
RNR_APSCCM = "rnrAPSCCM"
RNR_ACTIVTRAK = "rnrActivTrak"
RNR_APEXONE = "rnrApexOne"
RNR_ARANDA = "rnrAranda"
RNR_AVASTANTIVIRUS = "rnrAvastAntivirus"
RNR_BUFFERZONE = "rnrBUFFERZONE"
RNR_BIGFIX = "rnrBigFix"
RNR_BITLOCKER = "rnrBitLocker"
RNR_BTJUMPCLIENT = "rnrBtJumpClient"
RNR_CARBONBLACK = "rnrCarbonBlack"
RNR_CARBONBLACKEDR = "rnrCarbonBlackEDR"
RNR_CISCOAMP = "rnrCiscoAMP"
RNR_CISCOUMBRELLA = "rnrCiscoUmbrella"
RNR_CITRIXWORKSPACE = "rnrCitrixWorkspace"
RNR_CLOUDCODES = "rnrCloudCodes"
RNR_CROWDSTRIKE = "rnrCrowdStrike"
RNR_CYLANCEPROTECT = "rnrCylancePROTECT"
RNR_DEEPARMOR = "rnrDeepArmor"
RNR_DEEPINSTINCT = "rnrDeepInstinct"
RNR_DEFENDERATP = "rnrDefenderATP"
RNR_DEFENDERANTIVIRUS = "rnrDefenderAntivirus"
RNR_DELLATP = "rnrDellATP"
RNR_DELLDG = "rnrDellDG"
RNR_DELLENCRYPTION = "rnrDellEncryption"
RNR_DELLSUPPORTASSISTBUSINESS = "rnrDellSupportAssistBusiness"
RNR_DELLSUPPORTASSISTBUSINESSPCS = "rnrDellSupportAssistBusinessPCs"
RNR_DELLTRUSTEDDA = "rnrDellTrustedDA"
RNR_ECLINICALWORKS = "rnrEClinicalWorks"
RNR_ESESTPAV = "rnrESESTPAV"
RNR_ESETEPAV = "rnrESETEPAV"
RNR_F5VPN = "rnrF5VPN"
RNR_FIREEYE = "rnrFireEye"
RNR_FORCEPOINTONEDLP = "rnrForcePointOneDLP"
RNR_FORESCOUTSC = "rnrForescoutSC"
RNR_FORTICLIENTFABRICAGENT = "rnrFortiClientFabricAgent"
RNR_FORTICLIENTVPN = "rnrFortiClientVPN"
RNR_GLOBALPROTECT = "rnrGlobalProtect"
RNR_HALCYONAR = "rnrHALCYONAR"
RNR_HPTECHPULSE = "rnrHPTechPulse"
RNR_IMTLAZARUS = "rnrIMTLazarus"
RNR_IVANTIPATCHW = "rnrIVANTIPATCHW"
RNR_IVANTI_NEURO = "rnrIVANTI_NEURO"
RNR_INTUNE = "rnrIntune"
RNR_IVANTISAC = "rnrIvantiSAC"
RNR_JUMPCLOUDAGENT = "rnrJumpCloudAgent"
RNR_KASEYA = "rnrKASEYA"
RNR_LANDESK = "rnrLANDesk"
RNR_LENOVOUDC = "rnrLenovoUDC"
RNR_LENOVOVANTAGE = "rnrLenovoVantage"
RNR_LIGHTSPEED = "rnrLightspeed"
RNR_MCAFEEAGENT = "rnrMCAFEEAGENT"
RNR_MAGICENDPOINT = "rnrMagicEndpoint"
RNR_MALWAREBYTES = "rnrMalwarebytes"
RNR_MANAGEENGINE = "rnrManageEngine"
RNR_MCAFEEDE = "rnrMcAfeeDE"
RNR_NESSUS = "rnrNessus"
RNR_NETMOTION = "rnrNetMotion"
RNR_NETSFERE = "rnrNetSfere"
RNR_NETSKOPE = "rnrNetskope"
RNR_NORTON = "rnrNorton"
RNR_OPSWATCLIENT = "rnrOPSWATClient"
RNR_OCTOPUS = "rnrOctopus"
RNR_PLURILOCK = "rnrPLURILOCK"
RNR_PERSYSTENT = "rnrPersystent"
RNR_PIXARTMDM = "rnrPixartMDM"
RNR_PULSEVPN = "rnrPulseVPN"
RNR_QUALYS = "rnrQualys"
RNR_RAPID7 = "rnrRapid7"
RNR_SEPIOAGENT = "rnrSEPIOAGENT"
RNR_SYXSENSE = "rnrSYXSENSE"
RNR_SENTINELONE = "rnrSentinelOne"
RNR_SMARTDEPLOY = "rnrSmartDeploy"
RNR_SMARTEYE = "rnrSmartEye"
RNR_SOPHOSESC = "rnrSophosESC"
RNR_SYMANTECDLP = "rnrSymantecDLP"
RNR_SYMANTECEP = "rnrSymantecEP"
RNR_SYMANTECMA = "rnrSymantecMA"
RNR_TAEGIS = "rnrTAEGIS"
RNR_TERAMIND = "rnrTERAMIND"
RNR_TRUSTDELETE = "rnrTRUSTDELETE"
RNR_TANIUM = "rnrTanium"
RNR_UNOWHYMDM = "rnrUnowhyMDM"
RNR_VMWAREHORIZON = "rnrVmwareHorizon"
RNR_WINMAGIC = "rnrWinMagic"
RNR_WORKSPACEONE = "rnrWorkspaceONE"
RNR_XDR = "rnrXDR"
RNR_XM_CYBER = "rnrXMCyber"
RNR_ZIFTENZENITH = "rnrZIFTENZENITH"
RNR_ZTEDGE = "rnrZTEdge"
RNR_ZSCALER = "rnrZscaler"

# subset of fields from Absolute Device report that we will query
fields = [
    ABSOLUTE_ID,
    AGENT_VERSION,
    AGENT_STATUS,
    AVP_INFO,
    DEVICE_UID,
    DEVICE_NAME,
    ESP_INFO,
    GEO_DATA,
    LAST_CONNECTED_DATETIME_UTC,
    PUBLIC_IP,
    LOCAL_IP,
    USERNAME,
    NETWORK_ADAPTERS,
    OPERATING_SYSTEM,
    RNR_ANYCONNECT,
    RNR_APSCCM,
    RNR_ACTIVTRAK,
    RNR_APEXONE,
    RNR_ARANDA,
    RNR_AVASTANTIVIRUS,
    RNR_BUFFERZONE,
    RNR_BIGFIX,
    RNR_BITLOCKER,
    RNR_BTJUMPCLIENT,
    RNR_CARBONBLACK,
    RNR_CARBONBLACKEDR,
    RNR_CISCOAMP,
    RNR_CISCOUMBRELLA,
    RNR_CITRIXWORKSPACE,
    RNR_CLOUDCODES,
    RNR_CROWDSTRIKE,
    RNR_CYLANCEPROTECT,
    RNR_DEEPARMOR,
    RNR_DEEPINSTINCT,
    RNR_DEFENDERATP,
    RNR_DEFENDERANTIVIRUS,
    RNR_DELLATP,
    RNR_DELLDG,
    RNR_DELLENCRYPTION,
    RNR_DELLSUPPORTASSISTBUSINESS,
    RNR_DELLSUPPORTASSISTBUSINESSPCS,
    RNR_DELLTRUSTEDDA,
    RNR_ECLINICALWORKS,
    RNR_ESESTPAV,
    RNR_ESETEPAV,
    RNR_F5VPN,
    RNR_FIREEYE,
    RNR_FORCEPOINTONEDLP,
    RNR_FORESCOUTSC,
    RNR_FORTICLIENTFABRICAGENT,
    RNR_FORTICLIENTVPN,
    RNR_GLOBALPROTECT,
    RNR_HALCYONAR,
    RNR_HPTECHPULSE,
    RNR_IMTLAZARUS,
    RNR_IVANTIPATCHW,
    RNR_IVANTI_NEURO,
    RNR_INTUNE,
    RNR_IVANTISAC,
    RNR_JUMPCLOUDAGENT,
    RNR_KASEYA,
    RNR_LANDESK,
    RNR_LENOVOUDC,
    RNR_LENOVOVANTAGE,
    RNR_LIGHTSPEED,
    RNR_MCAFEEAGENT,
    RNR_MAGICENDPOINT,
    RNR_MALWAREBYTES,
    RNR_MANAGEENGINE,
    RNR_MCAFEEDE,
    RNR_NESSUS,
    RNR_NETMOTION,
    RNR_NETSFERE,
    RNR_NETSKOPE,
    RNR_NORTON,
    RNR_OPSWATCLIENT,
    RNR_OCTOPUS,
    RNR_PLURILOCK,
    RNR_PERSYSTENT,
    RNR_PIXARTMDM,
    RNR_PULSEVPN,
    RNR_QUALYS,
    RNR_RAPID7,
    RNR_SEPIOAGENT,
    RNR_SYXSENSE,
    RNR_SENTINELONE,
    RNR_SMARTDEPLOY,
    RNR_SMARTEYE,
    RNR_SOPHOSESC,
    RNR_SYMANTECDLP,
    RNR_SYMANTECEP,
    RNR_SYMANTECMA,
    RNR_TAEGIS,
    RNR_TERAMIND,
    RNR_TRUSTDELETE,
    RNR_TANIUM,
    RNR_UNOWHYMDM,
    RNR_VMWAREHORIZON,
    RNR_WINMAGIC,
    RNR_WORKSPACEONE,
    RNR_XDR,
    RNR_XM_CYBER,
    RNR_ZIFTENZENITH,
    RNR_ZTEDGE,
    RNR_ZSCALER
]
# Methods
GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'
PUT = 'PUT'

SCRIPT = 'Absolute Library'

# Used to map lower-level agent status codes to more easily understandable value
ACTIVE = 'Active'
INACTIVE = 'Inactive'
DISABLED = 'Disabled'
AGENT_STATUS_MAP = {'A': ACTIVE, 'D': DISABLED, 'I': INACTIVE}

# Antivirus protection status
PROTECTED = 'Protected'
NOT_PROTECTED = 'Not Protected'

# Used to map encryption status codes to more easily understandable value
NOT_ENCRYPTED = 'INST'
ENCRYPTED = "ENCR"
USED_SPACE_ENCRYPTED = 'USENCR'
ENCRYPTION_NO_DATA = ""
NOT_DETECTED = "UNKN"
DECRYPTION_IN_PROGRESS = "DECRINPR"
ENCRYPTION_IN_PROGRESS = "INPR"
SUSPENDED = 'SUSP'
DRIVES_ENCRYPTED_NONE = '0'
DRIVES_ENCRYPTED_ALL_LOCKED = '1'
DRIVES_ENCRYPTED_ALL_UNLOCKED = '2'
DRIVES_ENCRYPTED_SOME = '3'
DRIVES_ENCRYPTED_NO_DATA = '4'
ENCRYPTION_STATUS_MAP = {NOT_ENCRYPTED: 'Not Encrypted',
                         ENCRYPTED: 'Encrypted',
                         USED_SPACE_ENCRYPTED: 'Used Space Encrypted',
                         SUSPENDED: 'Suspended',
                         NOT_DETECTED: "Not Detected",
                         DECRYPTION_IN_PROGRESS: "Decryption In Progress",
                         ENCRYPTION_IN_PROGRESS: "Encryption In Progress",
                         ENCRYPTION_NO_DATA: "No Data"}

ALL_DRIVES_ENCRYPTED_STATUS_MAP = {DRIVES_ENCRYPTED_NONE: 'No Drives Encrypted',
                                   DRIVES_ENCRYPTED_ALL_LOCKED: 'All Drives Encrypted and Locked',
                                   DRIVES_ENCRYPTED_ALL_UNLOCKED: 'All Drives Encrypted and Unlocked',
                                   DRIVES_ENCRYPTED_SOME: 'Some Drives Encrypted',
                                   NO_DATA: "No Data"}

# Used to map more detailed and verbose app resilience status responses
# to smaller set of more easily understood categories
NOT_COMPLIANT_REASON = 'notCompliantReason'
NO_CURRENT_DATA = "NoCurrentData"
VERSION_CHECK = 'Version Unknown'
VERSION_NOT_COMPLIANT = "Version Not Compliant"
VERSION_HIGHER = 'Version Higher Than Policy'
VERSION_LOWER = 'Version Lower Than Policy'
NOT_INSTALLED = 'Not Installed'
PENDING_REBOOT = 'Pending Reboot'
CONFIGURATION_NOT_COMPLIANT = 'Configuration Not Compliant'
BITLOCKER_SERVICE_NOT_RUNNING = 'BitLocker Service Not Running'
BITLOCKER_CONFIGURATION_NOT_COMPLIANT = 'BitLocker Configuration Not Compliant'
MBAM_NOT_RUNNING = 'MBAM Service Not Running'
MBAM_NOT_VALID = 'MBAM Not Valid'
SCCM_SERVICE_NOT_RUNNING = 'SCCM Service Not Running'
SCCM_CONFIGURATION_NOT_COMPLIANT = "SCCM Configuration Not Compliant"
SCCM_ASSIGNED_SITE_NOT_FOUND = "SCCM Assigned Site Not Found"
WMI_NOT_RUNNING = 'WMI Service Not Running'
SERVICE_NOT_RUNNING = 'Service Not Running'
PROCESS_NOT_RUNNING = 'Process Not Running'
UNEXPECTED_PROCESS_RUNNING = 'Unexpected Process Running'
HEALTH_CHECK_ERROR = "Error Performing Health Check"
SERVICE_NOT_SIGNED = 'Service Not Signed'
FILE_NOT_SIGNED = 'File Not Signed'
SIGNING_VALIDATION_FAILED = 'Signing Validation Failed'
DRIVES_NOT_ENCRYPTED = 'Drives Not Encrypted'
DRIVES_WITH_NON_COMPLIANT_ENCRYPTION = "Drives Encrypted with Non-Compliant Encryption Type"
TPM_COMPATIBILITY_CHECK_FAILED = 'TPM Compatibility Check Failed'
TPM_NOT_ENABLED_ACTIVE = 'TPM Not Activated or Not Enabled'
SERVICE_SIGNATURE_NOT_VALID = 'Service Signature Not Valid'


NON_COMPLIANT_MAPPING = {
    NO_CURRENT_DATA: NO_DATA,
    NO_DATA: NO_DATA,
    'reboot pending': PENDING_REBOOT,               #Case 80 : Not Compliant - Reboot Pending
    'failed to find health check results': SERVICE_NOT_RUNNING,   #Case 49 : Service Not Running
    'process running and should not be': UNEXPECTED_PROCESS_RUNNING,     #Case 56 : Unexpected Process Running
    'admin share not found': CONFIGURATION_NOT_COMPLIANT,    #Case 36 should be checked firstly then repair failed
    "then repair failed": SERVICE_NOT_RUNNING,      #Case 75 : Repair failed -> Service Not Running
    'failed to repair wmi': WMI_NOT_RUNNING,
    'service file does not exist:': SERVICE_NOT_RUNNING,
    'service does not exist:': SERVICE_NOT_RUNNING,
    'service not running': SERVICE_NOT_RUNNING,
    'mbam agent not running': MBAM_NOT_RUNNING,
    'failed to read health check results': HEALTH_CHECK_ERROR,
    'process not running': PROCESS_NOT_RUNNING,
    'task not executed': HEALTH_CHECK_ERROR,
    'failed to create ': HEALTH_CHECK_ERROR,
    'script timeout': HEALTH_CHECK_ERROR,
    'script failed': HEALTH_CHECK_ERROR,
    'script does not have any content': HEALTH_CHECK_ERROR,
    'script is invalid': HEALTH_CHECK_ERROR,
    'script blocked': HEALTH_CHECK_ERROR,
    'failed to trigger': HEALTH_CHECK_ERROR,
    'version not found': VERSION_NOT_COMPLIANT,
    'version does not match': VERSION_CHECK,
    'version is older': VERSION_LOWER,
    'reinstall completed but the installer version was different from expected': VERSION_NOT_COMPLIANT,
    'application not installed': NOT_INSTALLED,                    #Case 12: Not Installed
    'hash does not match': VERSION_NOT_COMPLIANT,                  #Case 55 : VERSION_NOT_COMPLIANT
    'not installed': NOT_INSTALLED,
    'installer download failed': NOT_INSTALLED,
    'failed to download': NOT_INSTALLED,
    'failed to install': NOT_INSTALLED,
    'file not signed': FILE_NOT_SIGNED,                            #Case 51 : File Not Signed
    'not signed': SERVICE_NOT_SIGNED,
    'signature validation failed': SIGNING_VALIDATION_FAILED,
    'service has unexpected signer': SERVICE_SIGNATURE_NOT_VALID,  #Case 10: Service Signature Not Valid
    'unexpected signer': SERVICE_NOT_SIGNED,
    'unexpected startup type': CONFIGURATION_NOT_COMPLIANT,
    'registry key has unexpected value': CONFIGURATION_NOT_COMPLIANT,
    'registry key does not exist': CONFIGURATION_NOT_COMPLIANT,
    'drives not encrypted': DRIVES_NOT_ENCRYPTED,
    'drives with non-compliant encryption': CONFIGURATION_NOT_COMPLIANT,
    'tpm not activated': TPM_NOT_ENABLED_ACTIVE,
    'tpm not enable': TPM_NOT_ENABLED_ACTIVE,
    'failed to check tpm compatibility': TPM_COMPATIBILITY_CHECK_FAILED,
    'wmi not functional': WMI_NOT_RUNNING,
    'operating system not supported': CONFIGURATION_NOT_COMPLIANT,
    'bitlocker group policy conflict': CONFIGURATION_NOT_COMPLIANT,
    'invalid mbam': CONFIGURATION_NOT_COMPLIANT,
    'bitLocker user exempt from encryption in mbam policy': BITLOCKER_CONFIGURATION_NOT_COMPLIANT,
    'system drive must be ntfs': CONFIGURATION_NOT_COMPLIANT,
    'volume size is smaller than expected': CONFIGURATION_NOT_COMPLIANT,
    'system partition size is smaller than expected': CONFIGURATION_NOT_COMPLIANT,
    'failed to repair system partition': BITLOCKER_CONFIGURATION_NOT_COMPLIANT,
    'not configured': CONFIGURATION_NOT_COMPLIANT,            # Case 45,46 : CONFIGURATION_NOT_COMPLIANT
    'file not found': CONFIGURATION_NOT_COMPLIANT,            # Case 50 : CONFIGURATION_NOT_COMPLIANT - ABS-238123
    'inventory may be missing': CONFIGURATION_NOT_COMPLIANT,  # Case 43,44 : CONFIGURATION_NOT_COMPLIANT
    'assigned site not found': SCCM_ASSIGNED_SITE_NOT_FOUND,  # Case 42: SCCM_CONFIGURATION_NOT_COMPLIANT
    'ccm installation folder not found': CONFIGURATION_NOT_COMPLIANT,
    'one or several of these services not running': SERVICE_NOT_RUNNING
}

ITAR_COUNTRY_MAP = {'AF': 'AFGHANISTAN',
                    'AO': 'ANGOLA',
                    'BY': 'BELARUS',
                    'MM': 'BURMA',
                    'CN': 'CHINA (PRC)',
                    'CY': 'CYPRUS',
                    'CU': 'CUBA',
                    'HT': 'HAITI',
                    'IR': 'IRAN',
                    'IQ': 'IRAQ',
                    'LR': 'LIBERIA',
                    'LY': 'LIBYA',
                    'NG': 'NIGERIA',
                    'KP': 'NORTH KOREA',
                    'RW': 'RWANDA',
                    'SO': 'SOMALIA',
                    'SD': 'SUDAN',
                    'SY': 'SYRIA',
                    'VN': 'VIETNAM',
                    'YE': 'YEMAN',
                    'ZW': 'ZIMBABWE'
                    }
to_ct_props_map = {
    DEVICE_UID: "connect_absolute_device_uid",
    DEVICE_NAME:"connect_absolute_device_name",  
    AGENT_STATUS: "connect_absolute_status",
    AVP_STATUS: "connect_absolute_avp_status",
    ESP_STATUS: "connect_absolute_esp_status",
    IS_IN_ITAR: "connect_absolute_is_in_itar",
    CITY: "connect_absolute_location_city",
    COUNTRY: "connect_absolute_location_country",
    LAST_LOCATION_UPDATE_DATETIME_EPOCH: "connect_absolute_location_last_update",
    OS_NAME: "connect_absolute_os_name",
    OS_VERSION: "connect_absolute_os_version",
    NETWORK_ADAPTERS: "connect_absolute_network_adapters",
    COMPLIANT_APP: "connect_absolute_application_persitence",
    DAYS_OFFLINE: "connect_absolute_offline_days",
    LAST_CONNECTED_DATETIME_EPOCH: "connect_absolute_last_connected",
    PUBLIC_IP :"connect_absolute_public_address"
    }

# JWS VALIDATION URI
VALIDATE_URI = '/jws/validate'

# Params for Device report queries
DEVICE_REPORT_URI = '/v3/reporting/devices'
SCRIPTS_URI = '/v3/actions/reach/scripts'
MAX_PAGE_SIZE = 500
MAX_RETRIES = 3

# Params for End User Messaging
EUM_URI = "/v3/actions/requests/eum"
MIN_SNOOZE_TIMES = 1
MAX_SNOOZE_TIMES = 5
DIALOG = 'Dialog'
FULLSCREEN = "FullScreen"
MODES = [DIALOG, FULLSCREEN]
CAPTION_SUBMIT = 'Submit'
MAX_CAPTION_LEN = 14

# Params for Run Script
RUN_SCRIPT_URI = "/v3/actions/requests/reach"

# Params for SIEM events
SIEM_URI = '/v3/reporting/siem-events'

# Params for Freeze
FREEZE_URI = "/v3/actions/requests/freeze"
UNFREEZE_URI = "/v3/actions/freeze/remove-freeze"
DEFAULT_REQUEST_TITLE = 'Forescout - Absolute Connect'
DEFAULT_MESSAGE = 'Your device is not compliant with policy and has been frozen. Please contact your Administrator.'
HTML_DEFAULT = '''<!DOCTYPE html>
<html>
<body>

<h1>Absolute Freeze</h1>
<p>{}</p>

</body>
</html>'''
DEFAULT_MESSAGE_NAME = 'Device Not Compliant'
FREEZE_DEFINITION = 'freezeDefinition'
FREEZE_TYPE = 'deviceFreezeType'
SCHEDULED = 'Scheduled'
ON_DEMAND = 'OnDemand'
SCHEDULED_FREEZE_DATETIME_UTC = 'scheduledFreezeDateTimeUtc'
MAX_NAME_LEN = 1000

# Format for datetime strings
DT_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

application_status_mapping = {
    'NoCurrentData' : "No Current Data",
    'NotCompliant' : "Not Compliant"
}

application_enum_mapping = {
    'activtrak': 'ActivTrak Agent',
    'anyconnect': 'Cisco Secure Client',
    'anyconnectdemoversion': 'Cisco AnyConnect® Secure Mobility Client '
                            '(Demo version)',
    'apexone': 'Trend Micro Apex One™ Security Agent',
    'apsccm': 'Microsoft® SCCM',
    'aranda': 'Aranda Agent',
    'avastantivirus': 'Avast Antivirus',
    'bar': 'BAR Console AP app',
    'bartest': 'BAR Console AP app',
    'bigfix': 'HCL BigFix',
    'bitlocker': 'BitLocker®',
    'btjumpclient': 'BeyondTrust Jump™ Client',
    'bufferzone': 'BUFFERZONE® Security',
    'carbonblack': 'VMware Carbon Black Cloud™',
    'carbonblackedr': 'VMware Carbon Black EDR Sensor',
    'ciscoamp': 'Cisco® AMP for Endpoints Connector',
    'ciscoumbrella': 'Cisco Umbrella Roaming Client',
    'citrixworkspace': 'Citrix Workspace™',
    'cloudcodes': 'Plurilock CloudCodes',
    'crowdstrike': 'CrowdStrike Falcon®',
    'customapp': 'Custom App for AccountId 150656',
    'cylanceprotect': 'BlackBerry CylancePROTECT®',
    'deeparmor': 'SparkCognition EPP',
    'deepinstinct': 'Deep Instinct™',
    'defenderantivirus': 'Microsoft Defender Antivirus',
    'defenderatp': 'Microsoft Defender for Endpoint',
    'dellatp': 'Dell Advanced Threat Prevention',
    'delldda': 'Workspace ONE Deployment Agent',
    'delldda11': 'Dell DDA 1.1',
    'delldg': 'Dell Data Guardian',
    'dellencryption': 'Dell Encryption',
    'dellsupportassistbusinesspcs': 'Dell SupportAssist for Business PCs',
    'delltrustedda': 'Dell Trusted Device Agent',
    'eclinicalworks': 'eClinicalWorks Plug-in',
    'esetepav': 'ESET® Endpoint Antivirus',
    'f5vpn': 'F5® BIG-IP® Edge Client®',
    'fireeye': 'Trellix Endpoint Security Agent',
    'flexera': 'Flexera Inventory Agent',
    'forcepointonedlp': 'Forcepoint™ DLP Endpoint',
    'forescoutsc': 'Forescout SecureConnector',
    'forticlientfabricagent': 'FortiClient Fabric Agent',
    'forticlientvpn': 'FortiClient® VPN',
    'globalprotect': 'GlobalProtect™',
    'halcyonar': 'Halcyon Anti Ransomware',
    'hptechpulse': 'HP TechPulse',
    'idruideroomeagent': 'Idruide Roome Agent',
    'imtlazarus': 'IMTLazarus Agent',
    'intune': 'Microsoft Intune',
    'ivanti_neuro': 'Ivanti® Neurons Agent',
    'ivantipatchw': 'Ivanti® Security Controls',
    'ivantisac': 'Ivanti® Secure Access Client',
    'jumpcloudagent': 'JumpCloud Agent',
    'kaseya': 'Kaseya Agent',
    'landesk': 'Ivanti® Endpoint Manager',
    'lenovoudc': 'Lenovo Device Intelligence',
    'lenovovantage': 'Lenovo Vantage',
    'lightspeed': 'Lightspeed Smart Agent',
    'magicendpoint': 'WinMagic MagicEndpoint™',
    'malwarebytes': 'Malwarebytes Endpoint Agent',
    'manageengine': 'ManageEngine® Desktop Central',
    'mcafeeagent': 'Trellix ePolicy Orchestrator®',
    'mcafeede': 'McAfee® Drive Encryption',
    'nessus': 'Tenable Nessus Agent',
    'netcloud': 'NetCloud Echo Agent',
    'netmotion': 'Absolute Secure Access',
    'netsfere': 'NetSfere',
    'netskope': 'Netskope',
    'norton': 'Norton™ 360',
    'octopus': 'Octopus Desk',
    'opswatclient': 'OPSWAT Client',
    'persystent': 'Utopic Persystent',
    'pixartmdm': 'Pixart MDM',
    'plurilock': 'Plurilock Defend',
    'pulsevpn': 'Pulse Connect Secure',
    'qualys': 'Qualys Cloud Agent',
    'rapid7': 'Rapid7 Insight Agent',
    'sentinelone': 'SentinelOne™',
    'sepioagent': 'Sepio Agent',
    'smartdeploy': 'SmartDeploy Client',
    'smarteye': 'SmartEye',
    'sophosesc': 'Sophos Endpoint Protection',
    'symantecdlp': 'Symantec DLP',
    'symantecep': 'Symantec Endpoint Protection',
    'symantecma': 'Symantec Management Agent',
    'syxsense': 'Syxsense Responder',
    'taegis': 'Secureworks® Taegis™ Agent',
    'tanium': 'Tanium™',
    'teramind': 'Teramind Agent',
    'trustdelete': 'OneBe TRUST DELETE',
    'unowhymdm': 'Unowhy MDM',
    'vmwarehorizon': 'VMware Horizon Client',
    'winmagic': 'WinMagic SecureDoc™',
    'workspaceone': 'VMware Workspace ONE',
    'xdr': 'Cortex XDR™ Agent',
    'xmcyber': 'XM Cyber HaXM',
    'ziftenzenith': 'Ziften Zenith',
    'zoo': 'ZOO Application System',
    'zscaler': 'Zscaler™ Client Connector',
    'ztedge': 'Ericom ZTEdge'
    }

def is_email(s):
    try:
        name, domain = s.split('@')
        if len(domain.split('.')) != 2:
            return False
        return True
    except:
        pass
    return False

'''
Helper to convert simple string with ',' or ';' between parts to list
'''
def to_email_list(s):
    if not isinstance(s, str):
        return None
    delim = None
    for c in [',', ';']:
        if s.find(c) > 0:
            delim = c
            break
    if delim is None and is_email(s):
        l = [s]
    else:
        l = [item for item in s.split(delim) if is_email(item)]
        if len(l) == 0:
            l = None
    return l

'''
Helper to convert simple string with newlines between lines to minimally formatted HTML
'''
def to_html(s):
    HTML_START_TAG = '<HTML>'
    HTML_END_TAG = '</HTML>'
    if s[: len(HTML_START_TAG)].upper() != HTML_START_TAG:
        s = s.replace(HTML_END_TAG, '')
        s = s.replace(HTML_END_TAG.lower(), '')
    s = HTML_START_TAG + "<p>" + s.replace("\n", "<br>") + "</p>" + HTML_END_TAG
    return s

'''
Helper to build log message
'''
def to_message(script, msg, tup):
    if isinstance(script, str) and len(script) > 0:
        s = '{} - '.format(script)
    else:
        s = ""
    s += msg.format(*tup)
    return s

'''
Helper to build freeze passcode
'''
def to_passcode(device_uid, secret):
    passcode, error = None, None
    try:
        secret_b = bytes(secret, 'utf-8')  # unique per deployment
        device_uid_b = bytes(device_uid, 'utf-8')  # unique to the device
        hmac_sha256_hex = hmac.new(secret_b, device_uid_b, hashlib.sha256).hexdigest()
        passcode = int(hmac_sha256_hex, 16) % 100000000
    except Exception as e:
        error = 'Error generationg passcode: {}'.format(e)
    return passcode, error

'''
Helper to build query string to get script UID for script name
'''
def build_scripts_query_string(script_name, page_size=MAX_PAGE_SIZE, next_page=None):
    # if 'page_size' not int then set to MAX_PAGE_SIZE
    if not isinstance(page_size, int):
        page_size = MAX_PAGE_SIZE
    # otherwise make sure within 10-500 range inclusive
    else:
        page_size = max(page_size, 10)
        page_size = min(page_size, 500)
    # generate comma separated list using URL encoding for comma
    if isinstance(script_name, str):
        s = '?scriptNameContains={}'.format(script_name)
    else:
        s = ""
    if s == "":
        s += "?"
    else:
        s += "&"
    # append 'page_size' query param
    s += 'pageSize={:d}'.format(page_size)
    if isinstance(next_page, str):
        s += '&nextPage=' + next_page
    return s

'''
Helper to build query string for call to Absolute API
'''
def build_query_string(fields, filters=None, sort_by=None, desc=True, page_size=MAX_PAGE_SIZE, next_page=None):
    # if 'fields' is a string, convert to 1-item list
    if isinstance(fields, str):
        fields = [fields]
    # ignore 'sort_by' if not in 'fields'
    if isinstance(sort_by, str) and sort_by not in fields:
        sort_by = None
    # if 'desc' not boolean then set to 'True'
    if not isinstance(desc, bool):
        desc = True
    # if 'page_size' not int then set to MAX_PAGE_SIZE
    if not isinstance(page_size, int):
        page_size = MAX_PAGE_SIZE
    # otherwise make sure within 10-500 range inclusive
    else:
        page_size = max(page_size, 10)
        page_size = min(page_size, 500)
    # generate comma separated list using URL encoding for comma
    if isinstance(filters, str):
        s = filters + "&"
    else:
        s = ""
    if isinstance(fields, list):
        s += 'select=' + '%2C'.join(fields)
    # if valid 'sort_by' value then append and use 'desc' to determine whether descending or ascending
    if isinstance(sort_by, str):
        s += '&sortBy=' + sort_by
        if desc:
            s += '%3Cdesc'
        else:
            s += '%3Casc'
    # append 'page_size' query param
    s += '&pageSize={:d}'.format(page_size)
    if isinstance(next_page, str):
        s += '&nextPage=' + next_page
    return s

'''
Helper to sign 'payload'
'''
def sign(payload, secret, headers=None, algorithm='HS256'):
    signed_output, error = None, None
    try:
        signed_output = jwt.encode(payload, secret, algorithm, headers=headers)
        if not isinstance(signed_output, bytes):
            signed_output = bytes(signed_output, 'utf-8')
    except Exception as e:
        error = 'Exception generating signed output: {}'.format(e)
    return signed_output, error


'''
Helper to build request
'''
def build_request(token, secret, method, url, uri, query_string=None, payload=None):
    request, signed, error = None, None, None
    if payload is None:
        payload = {}
    if len(payload) > 0:
        payload = {"data": payload}
    if query_string is None:
        query_string = ""
    headers = {"alg": "HS256",
               "kid": token,
               "method": method,
               "content-type": "application/json",
               "uri": uri,
               "query-string": query_string,
               "issuedAt": round(time.time()) * 1000
               }
    logging.debug("{} - Payload: {} - Headers: {}".format(SCRIPT, payload, headers))
    signed, error = sign(payload, secret, headers)
    if error is None:
        try:
            request = urllib.request.Request(url, data=signed, headers={"content-type": "text/plain"})
        except Exception as e:
            error = 'Error building urllib.request.Request object: {}'.format(e)
    return request, signed, error


'''
Helper to send request built with above helper
'''
def send_request(request, opener, ssl_context=None):
    r, status, data, metadata, error = None, None, None, None, None
    if not opener is None:
        try:
            r = opener.open(request)
        except Exception as e:
            error = str(e)
    else:
        try:
            r = urllib.request.urlopen(request, context=ssl_context)
        except Exception as e:
            error = 'Error performing URL open for {}: {}'.format(request.get_full_url(), e)
    if r is not None:
        status = r.status
        try:
            r = json.loads(r.read())
            data = r.get('data')
            metadata = r.get('metadata')
            
        except Exception as e:
            error = 'Error reading response: {}'.format(e)
    return status, data, metadata, error

'''
Helper to build get request to script 
'''
def build_get_scripts_request(token, secret, url, query_string):
    uri = SCRIPTS_URI
    request, signed, error = build_request(token, secret, GET, url, uri, query_string)
    return request, signed, error

'''
Helper to get a 'page' of scripts from API; may have to be called multiple times and each call
returns 'next_page' token if available to be used in next call; defaults to MAX_PAGE_SIZE
to minimize number of calls needed
'''
def get_scripts_page(token, secret, url, next_page=None, page_size=MAX_PAGE_SIZE, opener=None, ssl_context=None):
    status, data, error = None, None, None
    query_string = build_scripts_query_string(None, page_size, next_page)
    request, signed, error = build_get_scripts_request(token, secret, url, query_string)
    if signed is not None and error is None:
        status, data, metadata, error = send_request(request, opener, ssl_context)
        try:
            next_page = metadata['pagination']['nextPage']
        except:
            next_page = None
    return status, data, next_page, error

'''
Gets scripts containing specified 'script_name'  
'''
def get_scripts(token, secret, url, script_name=None, next_page=None, page_size=MAX_PAGE_SIZE, opener=None, ssl_context=None, scripts=None):
    if scripts is None:
        scripts = []
    while True:
        status, data, next_page, error = get_scripts_page(token, secret, url, next_page=next_page, page_size=page_size,
                                                      opener=opener, ssl_context=ssl_context)
        if isinstance(data, list):
            if isinstance(scripts, list):
                if script_name is None:
                    scripts.extend(data)
                else:
                    for script in data:
                        sn_lower = script['scriptName'].lower()
                        if sn_lower == script_name.lower():
                            scripts.append(script)
        if error is not None:
            break
        if next_page is None:
            break

    return status, scripts, error

'''
Helper to get a 'page' of SIEM events from API; must be called multiple times and each call
returns 'next_page' token if available to be used in next call; defaults to MAX_PAGE_SIZE
to minimize number of calls needed
'''
def get_siem_events_page(token, secret, url, from_dt_utc=None, to_dt_utc=None,
                         next_page=None, page_size=MAX_PAGE_SIZE, opener=None, ssl_context=None):
    status, data, error = None, None, None
    request, signed, error = build_get_siem_events_request(token, secret, url, from_dt_utc, to_dt_utc,
                                                           page_size=page_size, next_page=None)
    if signed is not None and error is None:
        status, data, metadata, error = send_request(request, opener, ssl_context)
        try:
            next_page = metadata['pagination']['nextPage']
        except:
            next_page = None
    return status, data, next_page, error

'''
Gets SIEM events 
'''
def get_siem_events(token, secret, url, from_dt_utc=None, to_dt_utc=None, next_page=None, page_size=MAX_PAGE_SIZE,
                    opener=None, ssl_context=None, events=None):
    if events is None:
        events = []
    while True:
        status, data, next_page, error = get_siem_events_page(token, secret, url, from_dt_utc, to_dt_utc,
                                                      next_page=next_page, page_size=page_size,
                                                      opener=opener, ssl_context=ssl_context)
        if isinstance(data, list):
            events.extend(data)
        if error is not None:
            break
        if next_page is None:
            break
    return status, events, error

'''
Helper to build get request to device report URI '''
def build_get_devices_request(token, secret, url, query_string):
    uri = DEVICE_REPORT_URI
    request, signed, error = build_request(token, secret, GET, url, uri, query_string)
    return request, signed, error

'''
Helper to get a 'page' of devices from API; must be called multipe times and each call
returns 'next_page' token if available to be used in next call; defaults to MAX_PAGE_SIZE
to minimize number of calls needed
'''
def get_devices_page(token, secret, url, fields, filters=None, next_page=None, sort_by=None, desc=True,
                     page_size=MAX_PAGE_SIZE, opener=None, ssl_context=None):
    status, data, error = None, None, None
    query_string = build_query_string(fields, filters, sort_by, desc, page_size, next_page)
    request, signed, error = build_get_devices_request(token, secret, url, query_string)
    if signed is not None and error is None:
        status, data, metadata, error = send_request(request, opener, ssl_context)
        try:
            next_page = metadata['pagination']['nextPage']
        except:
            next_page = None
    return status, data, next_page, error

'''
Gets specified 'fields' for page of devices using provided 'filters' if any 
'''
def get_devices(token, secret, url, fields, filters=None, next_page=None, page_size=MAX_PAGE_SIZE, opener=None, ssl_context=None, devices=None):
    if devices is None:
        devices = []
    while True:
        status, data, next_page, error = get_devices_page(token, secret, url, fields, filters,
                                                      next_page=next_page, page_size=page_size,
                                                      opener=opener, ssl_context=ssl_context)
        if isinstance(data, list):
            devices.extend(data)
        if error is not None:
            break
        if next_page is None:
            break
    return status, devices, error

'''
Determines if device is compliant; currently based on Antivirus Protection (AVP) and Encryption (ESP) status
TO DO: enabled App Health to be optionally included as criteria
'''
def get_avp_esp_info(device):
    avp_status, avp_name, avp_version = NO_DATA, NO_DATA, NO_DATA
    esp_status, esp_name, esp_version, all_drives_encrypted = NO_DATA, NO_DATA, NO_DATA, NO_DATA
    try:
        avp_info = device[AVP_INFO]
        avp_name = avp_info.get(AVP_NAME, NO_DATA)
        if avp_name == NO_DATA:
            avp_status = NOT_PROTECTED
        else:
            avp_version = avp_info.get(AVP_VERSION, NO_DATA)
            avp_status = PROTECTED
    except:
        avp_status = NOT_PROTECTED
    try:
        esp_info = device[ESP_INFO]
        esp_name = esp_info.get(ESP_NAME, NO_DATA)
        esp_version = esp_info.get(ESP_VERSION, NO_DATA)
        esp_status = esp_info.get(ESP_STATUS, "")
        esp_status = ENCRYPTION_STATUS_MAP[esp_status]
        all_drives_encrypted = esp_info.get(ALL_DRIVES_ENCRYPTED, NO_DATA)
        all_drives_encrypted = ALL_DRIVES_ENCRYPTED_STATUS_MAP[all_drives_encrypted]
    except:
        pass
    return avp_status, avp_name, avp_version, esp_status, esp_name, esp_version, all_drives_encrypted

'''
Helper to get script_uid for script_name
'''
def get_script_uid(token, secret, url, script_name):
    script_uid = None
    if not isinstance(script_name, str):
        error = 'Script name must be string'
        return script_uid, error
    scripts = []
    status, scripts, error = get_scripts(token, secret, url, script_name, scripts=scripts)
    if len(scripts) == 0:
        error = "No script name found containing {}".format(script_name)
    elif len(scripts) > 1:
        error = "More than one script name found containing {}".format(script_name)
    else:
        script_uid = scripts[0]['scriptUid']
    return script_uid, error

'''
Helper to convert date string to epoch
'''
def date_string_to_epoch(date, fmt=DT_FORMAT):
    if date == NO_DATA:
        return None
    if date[-1] == 'Z':
        date = date[:-1]
    return int(datetime.strptime(date, fmt).timestamp())

'''
Helper to determine hours elapsed from datetime string to 'now'
'''
def hours_elapsed(dt_s, fmt='%Y-%m-%dT%H:%M:%S.%f'):
    elapsed, error = -1, None
    try:
        ts = date_string_to_epoch(dt_s)
        if(ts < 0):
            elapsed = -1
            error = 'Error getting hours elapsed since {}: {}'.format(dt_s, e)
        else:
            utc_now_ts = datetime.now(timezone.utc).timestamp()
            elapsed = max(1, round((utc_now_ts - ts) / 3600))
    except Exception as e:
        error = 'Error getting hours elapsed since {}: {}'.format(dt_s, e)
    return elapsed, error    

def get_days_offline(date):
    days, error = None, None
    if(date != NO_DATA):
        try:
            days, error = hours_elapsed(date)
            if(days > 0):
                days = round(days/24)
        except:
            pass
    return days, error

'''
Helpers to get location properties
'''
def get_location(device):
    try:
        location = device[GEO_DATA][LOCATION]
    except:
        location = None
    return location
        
def get_hours_in_location(location):
    dt_s, hours, error = NO_DATA, -1, None
    try:
        dt_s = location[LAST_UPDATE_DATETIME_UTC]
        hours, error = hours_elapsed(dt_s)
    except:
        pass
    return dt_s, hours, error

def get_city_country(location):
    city, country, country_code = NO_DATA, NO_DATA, NO_DATA
    try:
        geo_address = location[GEO_ADDRESS]
        city = geo_address[CITY]
        country = geo_address[COUNTRY]
        country_code = geo_address[COUNTRY_CODE]
        return city, country, country_code
    except:
        pass
    return city, country, country_code

'''
Parses geo info and calculates 'hours_in_locaton' based on 'last_location' (if provided)
and whether current location is same or not
'''
def parse_geo_info(device, last_location=None, fmt=DT_FORMAT):
    dt_s, city, country, country_code, hours_in_location = NO_DATA, NO_DATA, NO_DATA, NO_DATA, None
    try:
        location = get_location(device)
        dt_s, hours_in_location, error = get_hours_in_location(location)
        city, country, country_code = get_city_country(location)
    except:
        pass
    location = (dt_s, city, country, country_code, hours_in_location)
    return location

'''
Helper to get local and public ips as lists; returns empty list(s) if not found
'''
def get_ip_addresses(device):
    try:
        local_ips = device[LOCAL_IP]
        if isinstance(local_ips, str):
            local_ips = [local_ips]
    except:
        local_ips = []
    try:
        public_ips = device[PUBLIC_IP]
        if isinstance(public_ips, str):
            public_ips = [public_ips]
    except:
        public_ips = []
    return local_ips, public_ips

'''
Get name and mac address from network adapters; return mac as lower case without ':' or '.' delimiters
'''
def get_network_adapters(device):
    l = []
    try:
        for adapter in device[NETWORK_ADAPTERS]:
            d = {}
            try:
                mac = adapter[MAC_ADDRESS]
                if mac[:2] == '0x':
                    mac = mac[2:]
                mac = mac.replace(':', '').replace('.', '').lower()
                d[MAC] = mac
            except:
                d[MAC] = NO_DATA
            try:
                d[IPV4_ADDRESS] = adapter[IPV4_ADDRESS]
            except:
                d[IPV4_ADDRESS] = NO_DATA
            try:
                d[ADAPTER_TYPE] = adapter[ADAPTER_TYPE]
            except:
                d[ADAPTER_TYPE] = NO_DATA
            try:
                d[INSTALLED] = adapter[INSTALLED]
            except:
                d[INSTALLED] = NO_DATA
            try:
                d[NAME] = adapter[NAME]
            except:
                d[NAME] = NO_DATA
            l.append(d)
    except:
        pass
    return l

'''
Helper to get mac - if > 1 adapter, will try to return mac for adapter whose IPV4 address attribute matches local ip 
'''
def get_mac(device):
    mac = NO_DATA
    adapters = get_network_adapters(device)
    n_adapters = len(adapters)
    # if only one adapter then use its mac no matter what
    if n_adapters == 1:
        mac = adapters[0][MAC]
    elif n_adapters > 1:
        # if more than one adapter try to find adapter
        try:
            local_ip = device[LOCAL_IP]
        except:
            local_ip = None
        for i, adapter in enumerate(adapters):
            # if no mac data for this adapter skip
            if adapter[MAC] == NO_DATA:
                continue
            mac = adapter[MAC]
            # if local ip matches ipv4 address for adapter then use this mac
            if local_ip == adapter[IPV4_ADDRESS]:
                break
    return mac

def get_shortlisted_network_adapters(device):
    l = []
    try:
        for adapter in device[NETWORK_ADAPTERS]:
            d = {}
            try:
                d[NAME] = adapter[NAME]
            except:
                d[NAME] = NO_DATA
            try:
                d[IPV4_ADDRESS] = adapter[IPV4_ADDRESS]
            except:
                d[IPV4_ADDRESS] = NO_DATA
            try:
                d[DNS_HOSTNAME] = adapter[DNS_HOSTNAME]
            except:
                d[DNS_HOSTNAME] = NO_DATA
            try:
                d[DHCP_SERVER] = adapter[DHCP_SERVER]
            except:
                d[DHCP_SERVER] = NO_DATA
            try:
                mac = adapter[MAC_ADDRESS]
                if mac[:2] == '0x':
                    mac = mac[2:]
                mac = mac.replace(':', '').replace('.', '').lower()
                d[MAC] = mac
            except:
                d[MAC] = NO_DATA
            l.append(d)
    except:
        pass
    return l

'''
Extract version string from text Ex: 3.*.0 or 3.1.440.0
'''
def extract_version(text):
    version_pattern = re.compile(r'(\d+\*?\w*\.?\d*\*?\w*\.*\d*\*?\w*\.?\*?\w*)')
    versions = version_pattern.findall(text)
    if len(versions) < 2:
        raise ValueError("Expected 2 version found")
    return versions[0].strip("."), versions[1].strip(".")

'''
Compare version string, return true if equal or later version
'''
def compare_versions(v1, v2):
    v1_parts = v1.split('.')
    v2_parts = v2.split('.')
  
    # Check if all parts of version strings are numeric
    for part in v1_parts + v2_parts:
        if not part.isnumeric() and part != "*":
            raise ValueError(f"Invalid version part: {part}")

    v1_parts = [int(part) for part in v1_parts]
    v2_parts = [int(part) for part in (v2.replace('*', '0')).split('.')] + [0] * (len(v1_parts) - len((v2.replace('*', '0')).split('.')))

    return v1_parts >= v2_parts

def get_app_status_error_mapping(status_details):
    for key, value in NON_COMPLIANT_MAPPING.items():
        if(key.lower() in status_details.lower()):
            if(value == VERSION_CHECK):
                try:
                    actual, expected = extract_version(status_details)
                    if(compare_versions(actual, expected)):
                        return VERSION_HIGHER
                    else:
                        return VERSION_LOWER
                except:
                    return VERSION_NOT_COMPLIANT
            else:
                return value
    return UNKNOWN

'''
Gets persited app list
'''
def get_app_persistence_list(device):
    if not isinstance(device, dict):
        raise TypeError("Expected a dictionary, got {}".format(type(device)))
    app_list = []
    for key, value in device.items():
        if(key.startswith('rnr') and value.get('status') is not None):
            app = {}
            app_name = key.lstrip('rnr').lower()
            app[NAME] = application_enum_mapping.get(app_name, app_name)
            app_status = value.get(STATUS, NO_DATA)
            app[STATUS] = application_status_mapping.get(app_status, app_status)
            if(app_status == "Compliant"):
                app[STATUS_DETAILS] = NOT_APPLICABLE
            else:
                if(app_status != "NotCompliant"):
                    status_details = NO_DATA
                else:
                    status_details = value.get('statusDetails', NO_DATA)
                app[STATUS_DETAILS] = get_app_status_error_mapping(status_details=status_details)
            app_list.append(app)
    return app_list

'''
Gets properties for device
'''
def get_properties(device, script=None, fmt=DT_FORMAT):
    device_uid, username, agent_status, agent_version, os_name, os_version = NO_DATA, NO_DATA, NO_DATA, NO_DATA, NO_DATA, NO_DATA
    mac = NO_DATA
    last_location = None
    messages = []

    # get mac
    mac = get_mac(device)
    device[MAC] = mac

    #get shortlisted network adapters
    shortlisted_network_adapters = get_shortlisted_network_adapters(device)

    device[NETWORK_ADAPTERS] = shortlisted_network_adapters

    # get app list
    device_app_list = get_app_persistence_list(device)
    device[COMPLIANT_APP] = device_app_list
    
    device[DAYS_OFFLINE] = get_days_offline(device.get(LAST_CONNECTED_DATETIME_UTC, NO_DATA))[0]
    logging.debug("{} - Device days offline : {}".format(SCRIPT, device[DAYS_OFFLINE]))
    try:
        agent_status = device[AGENT_STATUS]
        agent_status = AGENT_STATUS_MAP[agent_status]
        device[AGENT_STATUS] = agent_status
    except:
        pass
    try:
        agent_version = device[AGENT_VERSION]
    except:
        pass
    if agent_status in [NO_DATA, DISABLED] or agent_version == NO_DATA:
        device[AGENT_INSTALLED] = False
    else:
        device[AGENT_INSTALLED] = True

    # get OS name and version attributes
    try:
        operating_system = device[OPERATING_SYSTEM]
        try:
            os_name = operating_system[NAME]
        except:
            pass
        try:
            os_version = operating_system[VERSION]
        except:
            pass
        device.pop(OPERATING_SYSTEM)
    except:
        pass
    device[OS_NAME] = os_name
    device[OS_VERSION] = os_version

    # get compliance attributes
    avp_status, avp_name, avp_version, esp_status, esp_name, esp_version, all_drives_encrypted = get_avp_esp_info(device)
    try:
        device.pop[AVP_INFO]
    except:
        pass
    try:
        device.pop[ESP_INFO]
    except:
        pass
    device[AVP_STATUS] = avp_status
    device[AVP_NAME] = avp_name
    device[AVP_VERSION] = avp_version
    device[ESP_STATUS] = esp_status
    device[ESP_NAME] = esp_name
    device[ESP_VERSION] = esp_name
    device[ALL_DRIVES_ENCRYPTED] = all_drives_encrypted

    # get location attributes
    last_update_dt_utc, city, country, country_code, hours_in_location = parse_geo_info(device, last_location=last_location, fmt=fmt)
    device[LAST_LOCATION_UPDATE_DATETIME_UTC] = last_update_dt_utc
    device[COUNTRY] = country
    device[CITY] = city
    if(hours_in_location > 0):
        device[HOURS_IN_LOCATION] = hours_in_location
    last_location_update_epoch = date_string_to_epoch(device.get(LAST_LOCATION_UPDATE_DATETIME_UTC, NO_DATA))
    device[LAST_LOCATION_UPDATE_DATETIME_EPOCH] = last_location_update_epoch
    last_connected_datetime_epoch = date_string_to_epoch(device.get(LAST_CONNECTED_DATETIME_UTC, NO_DATA))
    logging.debug("{} - LastConnected: {}".format(SCRIPT, last_connected_datetime_epoch))
    device[LAST_CONNECTED_DATETIME_EPOCH] = last_connected_datetime_epoch
    if country_code in ITAR_COUNTRY_MAP:
        device[IS_IN_ITAR] = True
    else:
        device[IS_IN_ITAR] = False
    # extract subset of updated 'device' properties that are connect properties
    properties = {}
    for key, value in device.items():
        if key in to_ct_props_map:
            properties[to_ct_props_map[key]] = value
    return mac, properties, messages

def build_get_siem_events_query_string(from_dt_utc=None, to_dt_utc=None, page_size=MAX_PAGE_SIZE, next_page=None, n_days=3):
    if from_dt_utc is None:
        dt = datetime.now(datetime.timezone.utc)
        ts = dt.timestamp()
        ts = ts - (n_days * 24 * 3600)
        from_dt_utc = datetime.fromtimestamp(ts)
        from_dt_utc = from_dt_utc.strftime(DT_FORMAT).split('.')[0]+'.000Z'

    if to_dt_utc is None:
        to_dt_utc = dt = datetime.now(datetime.timezone.utc)
        to_dt_utc = to_dt_utc.strftime(DT_FORMAT).split('.')[0]+'.000Z'

    # if 'page_size' not int then set to MAX_PAGE_SIZE
    if not isinstance(page_size, int):
        page_size = MAX_PAGE_SIZE
    # otherwise make sure within 10-500 range inclusive
    else:
        page_size = max(page_size, 10)
        page_size = min(page_size, 500)
    try:
        s = 'fromDateTimeUtc={}&toDateTimeUtc={}'.format(from_dt_utc, to_dt_utc)
        s += '&pageSize={:d}'.format(page_size)
        if isinstance(next_page, str):
            s += '&nextPage=' + next_page
        return s
    except:
        return None

def build_get_siem_events_request(token, secret, url, from_dt_utc=None, to_dt_utc=None, page_size=MAX_PAGE_SIZE, next_page=None):
    uri = SIEM_URI
    query_string = build_get_siem_events_query_string(from_dt_utc, to_dt_utc, page_size, next_page)
    request, signed, error = build_request(token, secret, GET, url, uri, query_string)
    return request, signed, error

def build_send_message_request(token, secret, url, device_uids, message, scheduled_dt_utc=None,
                               snooze_times=MIN_SNOOZE_TIMES, mode=DIALOG, caption=CAPTION_SUBMIT):
    uri = EUM_URI
    if isinstance(device_uids, str):
        device_uids = [device_uids]
    if scheduled_dt_utc is None:
        scheduled_dt_utc = ""
    if isinstance(snooze_times, int):
        snooze_times = min(snooze_times, 3)
        snooze_times = max(snooze_times, 1)
    else:
        snooze_times = MIN_SNOOZE_TIMES
    if mode not in MODES:
        mode = DIALOG
    if not isinstance(caption, str) or len(caption) == 0:
        caption = CAPTION_SUBMIT
    else:
        caption = caption[:MAX_CAPTION_LEN]

    payload = {
        'deviceUids': device_uids,
        "scheduledDateTimeUtc": scheduled_dt_utc,
        "message": message,
        "snoozeTimes": snooze_times,
        "displayMode": mode,
        "requestTitle" : DEFAULT_REQUEST_TITLE,
        "submitButtonCaption": caption
    }
    request, signed, error = build_request(token, secret, POST, url, uri, payload=payload)
    return request, signed, error

def build_run_script_request(token, secret, url, device_uids, script_uid, mac_cmd_line=None, win_cmd_line=None):
    uri = RUN_SCRIPT_URI
    if isinstance(device_uids, str):
        device_uids = [device_uids]

    # leave any scheduled or offline freezes in place
    payload = {
        "deviceUids": device_uids,
        "scriptUid": script_uid
    }
    if isinstance(mac_cmd_line, str) and mac_cmd_line != NO_DATA:
        payload['macScriptOption'] = {'commandLine': mac_cmd_line}
    if isinstance(win_cmd_line, str) and win_cmd_line != NO_DATA:
        payload['winScriptOption'] = {'commandLine': win_cmd_line}
    request, signed, error = build_request(token, secret, POST, url, uri, payload=payload)
    return request, signed, error

def run_script(token, secret, url, device_uids, script_uid, mac_cmd_line=None, win_cmd_line=None, opener=None, ssl_context=None):
    request, signed, error = build_run_script_request(token, secret, url, device_uids, script_uid, mac_cmd_line, win_cmd_line)
    status, data, metadata, error = send_request(request, opener, ssl_context)
    logging.debug('{} - Run script request status {} - error {} - data: {} - metadata: {}'.format(SCRIPT, status, error, data, metadata))
    return status, data, metadata, error

def build_unfreeze_request(token, secret, url, device_uids):
    uri = UNFREEZE_URI
    if isinstance(device_uids, str):
        device_uids = [device_uids]

    # leave any scheduled or offline freezes in place
    payload = {
        "deviceUids": device_uids
    }
    request, signed, error = build_request(token, secret, POST, url, uri, payload=payload)
    return request, signed, error


def build_freeze_request(token, secret, url, device_uids, passcode, message=None, message_name=None,
                         request_title=DEFAULT_REQUEST_TITLE, notification_emails=None):
    uri = FREEZE_URI
    if isinstance(device_uids, str):
        device_uids = [device_uids]
    if not isinstance(passcode, str):
        try:
            passcode = str(int(passcode))
        except:
            return None, 'Passcode value {} is not an integer'.format(passcode)
    else:
        try:
            int(passcode)
        except:
            return None, 'Passcode value {} is not an integer'.format(passcode)
    passcode_definition = {
        "option": "RandomForAll"
    }

    # if message not string, use default; convert to minimal HTML as needed
    if not isinstance(message, str):
        message = DEFAULT_MESSAGE

    #message = to_html(message)
    logging.debug("{} - message: {}".format(SCRIPT, message))
    # if message name not string with > 0 length, use default
    if not isinstance(message_name, str) or len(message_name) == 0:
        message_name = DEFAULT_MESSAGE_NAME
    message_name = message_name[: MAX_NAME_LEN]

    # if request title not string with > 0 length, use default
    if not isinstance(request_title, str) or len(request_title) == 0:
        request_title = DEFAULT_REQUEST_TITLE
    request_title = request_title[: MAX_NAME_LEN]

    # if notification emails not > 0 length list, set as ""
    if not isinstance(notification_emails, list) or len(notification_emails) == 0:
        notification_emails = ["duc@email.com"]

    freeze_definition = {FREEZE_TYPE: ON_DEMAND}

    payload = {
        "message": message,
        "messageName": message_name,
        "deviceUids": device_uids,
        "passcodeDefinition": passcode_definition,
        "requestTitle": request_title,
        "freezeDefinition": freeze_definition
    }
    
    logging.debug("{} - payload: {}".format(SCRIPT, payload))
    request, signed, error = build_request(token, secret, POST, url, uri, payload=payload)
    return request, signed, error


def freeze_device(token, secret, url, device_uids, passcode, message=None, message_name=None,
                  request_title=None, notification_emails=None, opener=None, ssl_context=None):
    data, metadata, error = None, None, None
    request, signed, error = build_freeze_request(token, secret, url, device_uids, passcode, message, message_name,
                                                  request_title, notification_emails)
    status, data, metadata, error = send_request(request, opener, ssl_context)
    logging.debug('{} - Freeze request status {} - error {} - data: {} - metadata: {}'.format(SCRIPT, status, error, data, metadata))
    return signed, data, metadata, error


def unfreeze_device(token, secret, url, device_uids, opener=None, ssl_context=None):
    data, metadata, error = None, None, None
    request, signed, error = build_unfreeze_request(token, secret, url, device_uids)

    status, data, metadata, error = send_request(request, opener, ssl_context)
    if(status == 202):
        error = None
    logging.debug('{} - Unfreeze request status {} - error {} - data: {} - metadata: {}'.format(SCRIPT, status, error, data, metadata))
    return signed, data, metadata, error


def send_message(token, secret, url, device_uids, message, scheduled_dt_utc=None, snooze_times=1, mode='Dialog',
                 caption=CAPTION_SUBMIT, opener=None, ssl_context=None):
    data, metadata, error = None, None, None
    request, signed, error = build_send_message_request(token, secret, url, device_uids, message, scheduled_dt_utc,
                                                        snooze_times, mode, caption)
    status, data, metadata, error = send_request(request, opener, ssl_context)
    logging.debug('{} - Send EUM message request status {} - error {} - data: {} - metadata: {}'.format(SCRIPT, status, error, data, metadata))
    return data, metadata, error

