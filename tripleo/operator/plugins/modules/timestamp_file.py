#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
module: timestamp_file
author:
  - "Alex Schultz (@mwhahaha)"
version_added: '2.9'
short_description: Take a copy of a file and append a timestamp
notes: []
description:
  - Take a copy of a file and append a timestamp
requirements:
  - None
options:
  path:
    description:
      - Path to file
    type: str
  remove:
    description:
      - Remove original file
    default: False
    type: bool
  date_format:
    description:
      - Timestamp format to use when appending to destination file
    default: "%Y-%m-%d_%H:%M:%S"
    type: str
"""
EXAMPLES = """
- name: Snapshot a file
  timestamp_file:
    path: /tmp/file.log
- name: Snapshot a file and remove original
  timestamp_file:
    path: /tmp/file.log
    remove: True
"""
RETURN = """
dest:
    description: Path to the new file
    returned: if changed
    type: str
    sample: "/tmp/file.log.2017-07-27_16:39:00"
"""

import json
import yaml

from ansible.plugins.action import ActionBase
from datetime import datetime


class ActionModule(ActionBase):
    def _get_args(self):
        options = yaml.safe_load(DOCUMENTATION)['options']
        missing = []
        args = {}

        for option, vals in options.items():
            if 'default' not in vals and not self._task.args.get(option, None):
                missing.add(option)
                continue
            args[option] = self._task.args.get(option, vals['default'])

        if missing:
            raise Exception('Missing required parameters: {}'.format(
                            ', '.join(missing)))
        return args

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        # parse args
        try:
            args = self._get_args()
        except Exception as e:
            result['failed'] = True
            result['msg'] = "Action failed: {}".format(e)
            return self._ensure_invocation(result)

        changed = False
        src_path = args['path']

        # check if file exists
        file_stat = self._execute_module(
            module_name='stat',
            module_args=dict(path=src_path),
            task_vars=task_vars
        )
        timestamp = datetime.now().strftime(args['date_format'])
        dest_path = '.'.join([src_path, timestamp])
        if file_stat.get('stat', {}).get('exists', False) is False:
            # file doesn't exist so we're done
            result.merge(dict(skipped=True))
            return self._ensure_invocation(result)

        # copy file out of the way
        copy_result = self._execute_module(
            module_name='copy',
            module_args=dict(src=src_path, dest=dest_path, remote_src=True),
            task_vars=task_vars
        )
        changed = True
        if bool(args['remove']) is True:
            # cleanup original file as requested
            file_result = self._execute_module(
                module_name='file',
                module_args=dict(path=src_path, state='absent'),
                task_vars=task_vars
            )

        result.merge(dict(dest=copy_result['dest'], changed=changed))
        return self._ensure_invocation(result)
