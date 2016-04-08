#
# (C) 2016  Matt Young <halcyondude@gmail.com>
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# File is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See <http://www.gnu.org/licenses/> for a copy of the
# GNU General Public License

#
#
#

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: execution_diag
version_added: "1.9"
short_description: task profiling and timing callback plugin for Ansible.

description:
   - dumps out callbacks called
   - coming soon: generates a diagnostics and analysis of playbook execution
   - [this version] does not use v2 hooks (there are many added) to maintain
     ability to be used on 1.9.  In addition, even if the callback is not whitelisted
     or otherwise loaded, it merely existing in the callback directory will cause failure
     as the loader blindly loads all callbacks.
'''

import pprint
import json
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    """
    This plugin generates a data file useful for diagnostics and analysis of playbook execution
    """
    CALLBACK_VERSION = 1.9
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'execution_diag'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

    def _log(self, msg):
        # TODO: make this better, handle varargs
        # note: display(self, msg, color=None, stderr=False, screen_only=False, log_only=False)
        self._display.display(msg)

    def _to_vars_s(self, thing):
        return pprint.pformat(vars(thing), indent=2)

    def _to_json_s(self, thing):
        return json.dumps(thing, sort_keys=True, indent=2, separators=(',', ': '))

####################################################################
#
# ansible-playbook invocation generally looks like...
#
#   playbook_on_start()
#   on_any()
#   set_play_context()
#   playbook_on_play_start()
#   on_any
#
#   FOR EACH TASK
#   playbook_on_task_start()
#   on_any()
#   runner_on_[ failed | ok | skipped | unreachable | no_hosts | async_poll | async_ok | async_failed ]()
#   on_any()
#   END FOR
#
####################################################################


#    def set_play_context(self, play_context):
#        self._log("set_play_context(self, play_context)")
#        self._log(self._to_vars_s(play_context))

    def on_any(self, *args, **kwargs):
        self._log("on_any(self, *args, **kwargs)")
        self._log("\ttype arg[0]: " + str(type(args[0])))
        for arg in args:
            self._log("\t(arg):" + str(arg) + " TYPE: " + str(type(arg)))

    def runner_on_failed(self, host, res, ignore_errors=False):
        self._log("runner_on_failed(self, host, res, ignore_errors=False)")

    def runner_on_ok(self, host, res):
        self._log("runner_on_ok( " + str(host) + ", " + str(res) + "\n" + self._to_json_s(res) + "\n)")

    def runner_on_skipped(self, host, item=None):
        self._log("runner_on_skipped(self, host, item=None)")

    def runner_on_unreachable(self, host, res):
        self._log("runner_on_unreachable(self, host, res)")

    def runner_on_no_hosts(self):
        self._log("runner_on_no_hosts(self)")

    def runner_on_async_poll(self, host, res, jid, clock):
        self._log("runner_on_async_poll(self, host, res, jid, clock)")

    def runner_on_async_ok(self, host, res, jid):
        self._log("runner_on_async_ok(self, host, res, jid)")

    def runner_on_async_failed(self, host, res, jid):
        self._log("runner_on_async_failed(self, host, res, jid)")

    def playbook_on_start(self):
        self._log("playbook_on_start(self)")

    def playbook_on_notify(self, host, handler):
        self._log("playbook_on_notify(self, host, handler)")

    def playbook_on_no_hosts_matched(self):
        self._log("playbook_on_no_hosts_matched(self)")

    def playbook_on_no_hosts_remaining(self):
        self._log("playbook_on_no_hosts_remaining(self)")

    def playbook_on_task_start(self, name, is_conditional):
        self._log("playbook_on_task_start( %s )" % str(name))

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        self._log("playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None)")

    def playbook_on_setup(self):
        self._log("playbook_on_setup(self)")

    def playbook_on_import_for_host(self, host, imported_file):
        self._log("playbook_on_import_for_host(self, host, imported_file)")

    def playbook_on_not_import_for_host(self, host, missing_file):
        self._log("playbook_on_not_import_for_host(self, host, missing_file)")

    def playbook_on_play_start(self, name):
        self._log("playbook_on_play_start( %s )" % str(name))

    def playbook_on_stats(self, stats):
        self._log("playbook_on_stats( %s )" % str(stats))
        self._log(self._to_vars_s(stats))

    def on_file_diff(self, host, diff):
        self._log("on_file_diff(self, host, diff)")

