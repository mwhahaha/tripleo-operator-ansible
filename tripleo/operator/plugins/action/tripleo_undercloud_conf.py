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

from ansible.errors import AnsibleActionFail
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase

import yaml

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
module: tripleo_undercloud_conf
author:
  - "Alex Schultz (@mwhahaha)"
version_added: '2.9'
short_description: Update a TripleO undercloud.conf with provided values
notes: []
description:
  - This module updates an undercloud.conf with the provided values. It can
    also copy a sample undercloud.conf if the file is not present. If the
    undercloud.conf does not exist, an error is thrown.
requirements:
  - None
options:
  path:
    description:
      - Path to undercloud.conf
    type: str
  values:
    description:
      - A dictionary representation of the values to configure with the top
        level key being the ini group and each of these contains a key, value
        dictionary of settings
    default: {}
    type: dict
  sample_path:
    description:
      - Path to undercloud.conf.sample on the remote host
    default: /usr/share/python-tripleoclient/undercloud.conf.sample
    type: str
  use_sample:
    description:
      - Copy a sample file in place and update using that as the base
    default: False
    type: bool
"""
EXAMPLES = """
- name: Update undercloud.conf
  tripleo_undercloud_config:
    path: /home/stack/undercloud.conf
    values:
      DEFAULT:
        debug: True
- name: Update undercloud.conf from sample
  tripleo_undercloud_config:
    path: /home/stack/undercloud.conf
    values:
      DEFAULT:
        debug: True
    sample_path: /my/custom/sample.conf
    use_sample: true
"""
RETURN = """
path:
    description: Path to the undercloud.conf file
    returned: always
    type: str
    sample: "/home/stack/undercloud.conf"
"""


class ActionModule(ActionBase):

    _VALID_ARGS = yaml.safe_load(DOCUMENTATION)['options']

    def _get_args(self):
        missing = []
        args = {}

        for option, vals in self._VALID_ARGS.items():
            if 'default' not in vals:
                if self._task.args.get(option, None) is None:
                    missing.append(option)
                    continue
                args[option] = self._task.args.get(option)
            else:
                args[option] = self._task.args.get(option, vals['default'])

        if missing:
            raise AnsibleActionFail('Missing required parameters: {}'.format(
                            ', '.join(missing)))
        return args

    def _file_exists(self, path, task_vars):
        file_stat = self._execute_module(
            module_name='stat',
            module_args=dict(path=path),
            task_vars=task_vars
        )
        if file_stat.get('stat', {}).get('exists', False) is False:
            raise AnsibleActionFail("{} does not exist.".format(path))

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        # parse args
        args = self._get_args()

        changed = False
        undercloud_path = args['path']
        use_sample = boolean(args.get('use_sample', False), strict=False)
        sample_path = args['sample_path']

        # check if undercloud.conf file exists
        try:
            self._file_exists(undercloud_path, task_vars)
        except AnsibleActionFail:
            if not use_sample:
                # skip failing because we'll copy the sample as our base
                raise

        if use_sample:
            self._file_exists(sample_path, task_vars)
            # copy sample file in place
            copy_result = self._execute_module(
                module_name='copy',
                module_args=dict(src=sample_path,
                                 dest=undercloud_path,
                                 remote_src=True),
                task_vars=task_vars
            )
            if copy_result.get('failed', False):
                return copy_result
            changed = copy_result.get('changed', False)

        for key, values in args['values'].items():
            for k, v in values.items():
                ini_result = self._execute_module(
                    module_name='ini_file',
                    module_args=dict(path=undercloud_path,
                                     section=key,
                                     option=k,
                                     value=v),
                    task_vars=task_vars)

                if ini_result.get('failed', False):
                    return ini_result
                if ini_result.get('changed', False):
                    # only mark changed if we actually set something
                    changed = True

        result['dest'] = undercloud_path
        result['changed'] = changed
        return result
