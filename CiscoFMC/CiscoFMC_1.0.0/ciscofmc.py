"""
Copyright © 2021 Forescout Technologies, Inc.
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
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
from requests.packages import urllib3
import base64
import logging
from urllib3.exceptions import InsecureRequestWarning


logging.debug('===>Starting Cisco FMC Class Script')

class CiscoFMC:
    token_occurrence = 0
    access_token = ''
    refresh_token = ''
    domains= []


    def __init__(self,fmc_server,user,passwd,ctx):
        self.fmc_server = fmc_server
        self.username= user
        self.passwd = passwd
        self.ctx = ctx
        logging.debug('===>Cisco FMC Class initialised')


    def get_auth_token(self):
        try:
            if CiscoFMC.token_occurrence == 0:
                self.generate_access_token()
                logging.debug(f'===>Cisco FMC Class Method generate_Access_token and Token Occurance:{CiscoFMC.token_occurrence}')
            elif CiscoFMC.token_occurrence < 3:
                self.generate_refresh_auth_token()
                logging.debug(f'===>Cisco FMC Class Method - Refresh_auth_token and Token Occurance:{CiscoFMC.token_occurrence}')
            else:
                self.generate_refresh_auth_token()
                CiscoFMC.token_occurrence = 0
                logging.debug(f'===>Cisco FMC Class Method - Refresh_auth_token and Token Occurance:{CiscoFMC.token_occurrence}')

        except Exception as e:
            logging.debug(f"===>Cisco FMC Class- Error get_auth_token - Verify the Crendentials")



    def generate_access_token(self):
        api_path = "/api/fmc_platform/v1/auth/generatetoken"
        url = f'https://{self.fmc_server}' + api_path

        credentials = ('%s:%s' % (self.username, self.passwd))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        authstring = ("Basic %s" % encoded_credentials.decode("ascii"))
        headers = {'Authorization': authstring,'Accept': 'application/json', 'Content-Type': 'application/json'}

        try:
            if not self.ctx:
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

            resp = requests.post(url, headers=headers, verify=self.ctx)
            if resp.status_code == 200 | 204:
                CiscoFMC.access_token = resp.headers['X-auth-access-token']
                CiscoFMC.refresh_token = resp.headers['X-auth-refresh-token']
                CiscoFMC.domains = resp.headers['DOMAINS']
                CiscoFMC.token_occurrence += 1
                logging.debug("Cisco FMC Class Method:generate_access_token - Token successfully generated")

            else:
                CiscoFMC.token_occurrence = 0
                logging.debug(f'Cisco FMC Class Method:generate_access_token - Cannot generate auth token. Status code is {resp.status_code}')

        except requests.exceptions.HTTPError as e:
            logging.debug(f'Cannot connect the FMC HTTPError: {e}')
        except requests.exceptions.ConnectionError as e:
            logging.debug(f'Cannot connect the FMC ConnectionError : {e}')
        except requests.exceptions.Timeout as e:
            logging.debug(f'Cannot connect the FMC Timeout Error : {e}')
        except Exception as e:
            logging.debug(f"===>Cisco FMC Class Failed - Error - Verify the FMC IP/FQDN \n{e}")




    def generate_refresh_auth_token(self):
        api_path = "/api/fmc_platform/v1/auth/refreshtoken"
        url = f'https://{self.fmc_server}' + api_path
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                   'X-auth-access-token':CiscoFMC.access_token,'X-auth-refresh-token':CiscoFMC.refresh_token}

        try:
            if not self.ctx:
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

            resp = requests.post(url, headers=headers, verify=self.ctx)
            if resp.status_code == 200|204:
                CiscoFMC.access_token = resp.headers['x-auth-access-token']
                CiscoFMC.refresh_token = resp.headers['x-auth-refresh-token']
                CiscoFMC.domain = resp.headers['DOMAINS']
                CiscoFMC.token_occurrence += 1
                logging.debug("Cisco FMC Class Method:generate_refresh_auth_token - Token successfully generated")

            else:
                CiscoFMC.token_occurrence = 0
                logging.debug(f'Cisco FMC Class Method:generate_refresh_auth_token- Cannot generate auth token verify the credentials. Status code is {resp.status_code}')

        except requests.exceptions.HTTPError as e:
            logging.debug(f'Cannot connect the FMC HTTPError: {e}')
        except requests.exceptions.ConnectionError as e:
            logging.debug(f'Cannot connect the FMC ConnectionError : {e}')
        except requests.exceptions.Timeout as e:
            logging.debug(f'Cannot connect the FMC Timeout Error : {e}')
        except Exception as e:
            logging.debug(f"===>Cisco FMC Class Failed -Error - Verify the FMC IP/FQDN \n{e}")

logging.debug('===>Ending Cisco FMC Class Script')




