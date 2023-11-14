"""
Copyright © 2020 Forescout Technologies, Inc.

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

import logging


logging.debug("===> Starting Cisco VM Test Script")

# Defining Variables
response = dict()

try:
    url = params["connect_ciscovm_url"]
    token = params["connect_ciscovm_token"]
    uid = params["connect_ciscovm_uid"]
    client = ciscovm_helpers.CVMHTTPClient(url=url, auth_token=token, uid=uid)
    client_response = client.ping()
    response = {
        "succeeded": True,
        "result_msg": f"Connected to '{client.full_url}'.",
    }
except Exception as e:
    response = {
        "succeeded": False,
        "result_msg": str(e),
    }

logging.debug("===> End Cisco VM Test Script")
