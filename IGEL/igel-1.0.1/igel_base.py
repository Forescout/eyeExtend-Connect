'''
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
'''

import contextlib
import json
import logging
import random
import requests
import time

VERSION = '1.0.1'

# Mapping between IGEL response fields to Forescout Connect App properties
IGEL_TO_CT_PROPS_MAP = {
    'unitID': 'connect_igel_unit_id',
    'mac': 'connect_igel_mac',
    'firmwareID': 'connect_igel_firmware_id',
    'last_ip': 'connect_igel_last_ip',
    'deviceAttributes': 'connect_igel_device_attributes',
    'id': 'connect_igel_id',
    'name': 'connect_igel_name',
    'parentID': 'connect_igel_parent_id',
    'movedToBin': 'connect_igel_moved_to_bin',
    'objectType': 'connect_igel_object_type',
    'links': 'connect_igel_links'
}


class IgelAsset:
    def __init__(self, asset_dict):
        self.asset_info = asset_dict


class IgelRequest:
    pass
