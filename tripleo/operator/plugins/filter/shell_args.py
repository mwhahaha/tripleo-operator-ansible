#!/usr/bin/env python
# Copyright 2019 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


class FilterModule(object):
    def filters(self):
        return {
            'shell_arg_enabled': self.shell_arg_enabled,
            'shell_arg_list': self.shell_arg_list,
            'shell_logging_path': self.shell_logging_path
        }

    def shell_arg_enabled(self, arg, enabled=False):
        if not enabled:
            return ''
        return arg

    def shell_arg_list(self, arg, parameter=None):
        if not isinstance(arg, (list, tuple)):
            arg = [arg]
        return_value = []
        for a in arg:
            if parameter:
                return_value.append("{} {}".format(parameter, a))
            else:
                return_value.append(a)
        return ' '.join(return_value)

    def shell_logging_path(self, location, combine=True, enabled=False):
        output = ''
        if not enabled:
            return output
        if combine:
            output = "{} {}".format(output, '2>&1')
        return "{} >{}".format(output, location)
