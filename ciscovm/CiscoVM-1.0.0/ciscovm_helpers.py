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
import functools
import hashlib
import json
import time
from datetime import datetime, timezone

import requests


class CVMHTTPClient:
    """Cisco Vulnerability Management HTTP client"""
    CHECK_EVENT_TYPE = "ping"
    POST_EVENT_TYPE = "job-results"
    # Create a custom Retry object with max retries set to 3
    RETRY_STRATEGY = {
        "total": 1,
        "backoff_factor": 1,
        "status_forcelist": [408, 429, 500, 502, 503, 504]
    }
    TIMEOUT_SECONDS = 100

    def __init__(self, url: str, uid: str, auth_token: str):
        self.full_url = f"{url.strip('/')}/{uid.strip('/').strip()}"
        self.auth_token = auth_token.strip()

    def _generate_headers(self, event_type: str = CHECK_EVENT_TYPE) -> dict:
        """Generate request headers"""
        return {
            "X-Forescout-Event": event_type,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

    def with_retries(func):
        """Adds retry logic to request"""
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            for attempt in range(self.RETRY_STRATEGY["total"]):
                response = func(self, *args, **kwargs)
                if response.status_code in self.RETRY_STRATEGY["status_forcelist"]:
                    # Retry request with backoff delay
                    delay = self.RETRY_STRATEGY["backoff_factor"] * (2 ** attempt)
                    msg = f"Status code: {response.status_code}"
                    logging.debug(f"{msg}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                break
            response.raise_for_status()
            return response
        return wrap

    @with_retries
    def ping(self) -> requests.Response:
        """Check connection to the service"""
        return requests.post(self.full_url, headers=self._generate_headers(),
                             timeout=self.TIMEOUT_SECONDS)

    @with_retries
    def post(self, data: dict) -> requests.Response:
        """Send data"""
        return requests.post(
            self.full_url,
            headers=self._generate_headers(self.POST_EVENT_TYPE),
            data=json.dumps(data),
            timeout=self.TIMEOUT_SECONDS
        )


class DataGenerator:
    """Generate output data"""

    TS_KEY = "last_seen_time"
    TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    FS_PROP_FOR_CVM = (
        "mac",
        "ip",
        "dhcp_hostname",
        "vendor_classification",
        "vendor",
        "prim_classification",
        "hostname",
        "os_classification",
        "segment_path",
        "nbthost"
    )
    HASH_KEY = "connect_ciscovm_exported_hash"

    def __init__(self, fs_data: dict):
        self._payload = None
        self.payload_hash = None
        self.exported_hash = fs_data.get(self.HASH_KEY)

        self.set_payload(fs_data)
        self.set_payload_hash()

    """Payload getter"""
    def get_payload(self, add_timestamp: bool=False):
        if add_timestamp is True:
            return {**self._payload, **{self.TS_KEY: self.generate_timestamp()}}
        return self._payload

    """Payload setter"""
    def set_payload(self, data):
        """Generate output JSON"""
        payload = dict()
        for field_name in self.FS_PROP_FOR_CVM:
            payload[field_name] = data.get(field_name)

        self._payload = payload

    """Generate current timestamp"""
    def generate_timestamp(self):
        return datetime.now(timezone.utc).strftime(self.TS_FORMAT)

    """Payload hash setter"""
    def set_payload_hash(self):
        self.payload_hash = hashlib.sha256(json.dumps(self._payload, sort_keys=True).encode()).hexdigest()

    """Define if previous payload hash differs from the current"""
    def payload_change_detected(self):
        return self.payload_hash != self.exported_hash
