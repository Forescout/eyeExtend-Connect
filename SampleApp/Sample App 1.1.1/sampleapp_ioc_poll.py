import urllib.request
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# CONFIGURATION
url = params.get("connect_sampleapp_url")  # Server URL

#ADDITIONAL FUNCTIONS FOR PROCESSING DATA
def get_ioc_infos():
    # This is sample data.
    # The real one should be retrieved from 3rd party via API calls
    # and processed to be in correct format for IOC data
    infos = [
        {
            "name": "IOC Test 2",
            "hash_type": "ShA256",
            "hash": "4747d091f230bf409af6a42c32cca30d845541d2c3200bb275f0fa179bd5e999",
            "severity": "medium",
            "file_name": "test_file_2.exe",
            "file_exists": {
                "file_name": ["test_file_2.exe"],
                "file_path": ["C:\\test2"]
            },
            "cnc": "10.1.1.10",
            "dns": ["query1", "query2", ""],
            "process": {
                "process_name": ["test_process_1", "test_process_2"],
                "process_hash": ["process_hash_1","process_hash_2"],
                "process_hash_type": ["sha1", "none"]
            }
        },
        {
            "date": 1621571367000,
            "name": "IOC Test 3",
            "hash": "2e8d4a6fedf90e265d2370a543b4fd2a",
            "hash_type": "md5",
            "platform": "Windows",
            "file_name": "test_file_3.exe",
            "file_size": 10,
            "severity": "low"
        }
    ]
    return infos

response = {}
logging.debug("SampleApp IOC polling.")
# Check if we have valid auth token or not before processing.
if params.get("connect_authorization_token"):
    # ***** PART 2 - RETRIEVE IOC DATA FROM 3RD PARTY VIA REQUESTS ***** #
    jwt_token = params.get("connect_authorization_token")
    """
    Set additional parameters required for the requests such as URL, headers, etc...
    """
    try:
        """
        Use your own codes to construct the requests to get IOC data as well as 
        process the request response for the final data to pass to the response dictionary.
        In this example, we assume that the API calls and data parsing are completed.
        We already have IOC data ready for passing into response.
        
        For IOC polling, the response dictionary must contain a dictionary or a list of dictionary called "ioc", 
        which contains IOC information (single IOC or multiple IOCs respectively). 
        Each IOC should be formatted as a dictionary with four mandatory keys of "name", "file_name", "hash" and "severity".
        To get more details about "ioc" response format, please refer to Connect help file.
        The full response object, for example would be:
        {"ioc": {
            "name": "IOC Test 1",
            "hash_type": "Sha256",
            "hash": "4747d091f230bf409af6a42c32cca30d845541d2c3200bb275f0fa179bd5e999",
            "severity": "low",
            "file_name": "cscript.exe"
            }
        }
        or
        {"ioc": 
            [
                {
                "name": "IOC Test 1",
                "hash_type": "Sha256",
                "hash": "4747d091f230bf409af6a42c32cca30d845541d2c3200bb275f0fa179bd5e999",
                "severity": "medium",
                "file_name": "cscript.exe"
                "file_size": 44
                },
                {
                "name": "IOC Test 2",
                "hash_type": "md5",
                "hash": "2e8d4a6fedf90e265d2370a543b4fd2a",
                "severity": "low",
                "file_name": "cscript.exe",
                "file_exists": {'file_name': 'cscript.exe', 'file_path': 'c:\\windows\\system32\\'}
                "cnc": ["8.8.8.8", "9.9.9.9"]
                },
            ]
        }
        """
        ioc_infos = get_ioc_infos()
        if ioc_infos:
            response["ioc"] = ioc_infos
        else:
            response["error"] = "No IOC data available"
    except Exception as e:
        response["error"] = "Could not retrieve IOC data."
        logging.debug("Get error: {}".format(str(e)))
else:
    response["error"] = "Unauthorized"
