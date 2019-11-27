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

import mock

from ansible.errors import AnsibleActionFail
from ansible.playbook.play_context import PlayContext

from tripleo.operator.tests import base as tests_base
from tripleo.operator.plugins.action import tripleo_undercloud_conf


class TestTripleoUndercloudConf(tests_base.TestCase):

    def test_run(self):
        mock_task = mock.MagicMock()
        mock_task.async_val = None
        mock_task.action = "tripleo_undercloud_conf"
        mock_task.args = dict(path='foo.conf',
                              values={'DEFAULT': {'undercloud_debug': True}},
                              sample_path='bar.conf',
                              use_sample=True)
        mock_connection = mock.MagicMock()
        play_context = PlayContext()

        action = tripleo_undercloud_conf.ActionModule(mock_task,
                                                      mock_connection,
                                                      play_context,
                                                      None,
                                                      None,
                                                      None)

        mock_exists = mock.MagicMock()
        action._file_exists = mock_exists
        mock_execute = mock.MagicMock()
        mock_execute.side_effect = [{'failed': False},
                                    {'failed': False, 'changed': True}]
        action._execute_module = mock_execute

        result = action.run()

        exist_calls = [mock.call('foo.conf', {}),
                       mock.call('bar.conf', {})]
        self.assertEqual(2, mock_exists.call_count)
        mock_exists.assert_has_calls(exist_calls)

        execute_calls = [
            mock.call(module_args={'src': 'bar.conf',
                                   'dest': 'foo.conf',
                                   'remote_src': True},
                      module_name='copy',
                      task_vars={}),
            mock.call(module_args={'path': 'foo.conf',
                                   'section': 'DEFAULT',
                                   'option': 'undercloud_debug',
                                   'value': True},
                      module_name='ini_file',
                      task_vars={})
        ]
        self.assertEqual(2, mock_execute.call_count)
        mock_execute.assert_has_calls(execute_calls)

        expected_result = {'dest': 'foo.conf', 'changed': True}
        self.assertEqual(expected_result, result)

    def test_run_no_changes(self):
        mock_task = mock.MagicMock()
        mock_task.async_val = None
        mock_task.action = "tripleo_undercloud_conf"
        mock_task.args = dict(path='foo.conf',
                              values={'DEFAULT': {'undercloud_debug': True}},
                              sample_path='bar.conf',
                              use_sample=True)
        mock_connection = mock.MagicMock()
        play_context = PlayContext()

        action = tripleo_undercloud_conf.ActionModule(mock_task,
                                                      mock_connection,
                                                      play_context,
                                                      None,
                                                      None,
                                                      None)

        mock_exists = mock.MagicMock()
        action._file_exists = mock_exists
        mock_execute = mock.MagicMock()
        mock_execute.side_effect = [{'failed': False},
                                    {'failed': False, 'changed': False}]
        action._execute_module = mock_execute

        result = action.run()

        exist_calls = [mock.call('foo.conf', {}),
                       mock.call('bar.conf', {})]
        self.assertEqual(2, mock_exists.call_count)
        mock_exists.assert_has_calls(exist_calls)

        execute_calls = [
            mock.call(module_args={'src': 'bar.conf',
                                   'dest': 'foo.conf',
                                   'remote_src': True},
                      module_name='copy',
                      task_vars={}),
            mock.call(module_args={'path': 'foo.conf',
                                   'section': 'DEFAULT',
                                   'option': 'undercloud_debug',
                                   'value': True},
                      module_name='ini_file',
                      task_vars={})
        ]
        self.assertEqual(2, mock_execute.call_count)
        mock_execute.assert_has_calls(execute_calls)

        expected_result = {'dest': 'foo.conf', 'changed': False}
        self.assertEqual(expected_result, result)

    def test_run_missing_target_no_sample(self):
        mock_task = mock.MagicMock()
        mock_task.async_val = None
        mock_task.action = "tripleo_undercloud_conf"
        mock_task.args = dict(path='foo.conf',
                              values={'DEFAULT': {'undercloud_debug': True}},
                              sample_path='bar.conf',
                              use_sample=False)
        mock_connection = mock.MagicMock()
        play_context = PlayContext()

        action = tripleo_undercloud_conf.ActionModule(mock_task,
                                                      mock_connection,
                                                      play_context,
                                                      None,
                                                      None,
                                                      None)

        mock_exists = mock.MagicMock()
        action._file_exists = mock_exists
        mock_exists.side_effect = AnsibleActionFail('fail')

        self.assertRaises(AnsibleActionFail, action.run)

    def test_run_missing_target_missing_sample(self):
        mock_task = mock.MagicMock()
        mock_task.async_val = None
        mock_task.action = "tripleo_undercloud_conf"
        mock_task.args = dict(path='foo.conf',
                              values={'DEFAULT': {'undercloud_debug': True}},
                              sample_path='bar.conf',
                              use_sample=True)
        mock_connection = mock.MagicMock()
        play_context = PlayContext()

        action = tripleo_undercloud_conf.ActionModule(mock_task,
                                                      mock_connection,
                                                      play_context,
                                                      None,
                                                      None,
                                                      None)

        mock_exists = mock.MagicMock()
        action._file_exists = mock_exists
        mock_exists.side_effect = AnsibleActionFail('fail')

        self.assertRaises(AnsibleActionFail, action.run)
