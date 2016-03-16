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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: execution_diag
version_added: "2.0"
short_description: task profiling and timing callback plugin

description:
   - generates a data file useful for diagnostics and analysis of playbook execution
'''

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    """
    This plugin generates a data file useful for diagnostics and analysis of playbook execution
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'execution_diag'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

    def _log(self, msg):
        # TODO: make this better, handle varargs
        # note: display(self, msg, color=None, stderr=False, screen_only=False, log_only=False)
        self._display.display(msg)

####################################################################
####################################################################
####################################################################


    def set_play_context(self, play_context):
        self._log("set_play_context(self, play_context)")
        self._log("\t" + str(play_context))

    def on_any(self, *args, **kwargs):
        self._log("on_any(self, *args, **kwargs)")
        self._log("\t" + str(args))
        self._log("\t" + str(kwargs))

    def runner_on_failed(self, host, res, ignore_errors=False):
        self._log("runner_on_failed(self, host, res, ignore_errors=False)")

    def runner_on_ok(self, host, res):
        self._log("runner_on_ok(self, host, res)")

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
        self._log("playbook_on_task_start(self, name, is_conditional)")
        self._log("\t" + str(name))

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        self._log("playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None)")

    def playbook_on_setup(self):
        self._log("playbook_on_setup(self)")

    def playbook_on_import_for_host(self, host, imported_file):
        self._log("playbook_on_import_for_host(self, host, imported_file)")

    def playbook_on_not_import_for_host(self, host, missing_file):
        self._log("playbook_on_not_import_for_host(self, host, missing_file)")

    def playbook_on_play_start(self, name):
        self._log("playbook_on_play_start(self, name)")

    def playbook_on_stats(self, stats):
        self._log("playbook_on_stats(self, stats)")

    def on_file_diff(self, host, diff):
        self._log("on_file_diff(self, host, diff)")

    ####### V2 METHODS, by default they call v1 counterparts if possible ######
    def v2_on_any(self, *args, **kwargs):
        self._log("v2_on_any(self, *args, **kwargs)")
        self.on_any(args, kwargs)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._log("v2_runner_on_failed(self, result, ignore_errors=False)")
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)

    def v2_runner_on_ok(self, result):
        self._log("v2_runner_on_ok(self, result)")
        host = result._host.get_name()
        self.runner_on_ok(host, result._result)

    def v2_runner_on_skipped(self, result):
        self._log("v2_runner_on_skipped(self, result)")
        # TODO: C is not a defined here
        if C.DISPLAY_SKIPPED_HOSTS:
            host = result._host.get_name()
            self.runner_on_skipped(host, self._get_item(getattr(result._result,'results',{})))

    def v2_runner_on_unreachable(self, result):
        self._log("v2_runner_on_unreachable(self, result)")
        host = result._host.get_name()
        self.runner_on_unreachable(host, result._result)

    def v2_runner_on_no_hosts(self, task):
        self._log("v2_runner_on_no_hosts(self, task)")
        self.runner_on_no_hosts()

    def v2_runner_on_async_poll(self, result):
        self._log("v2_runner_on_async_poll(self, result)")
        host = result._host.get_name()
        jid = result._result.get('ansible_job_id')
        #FIXME, get real clock
        clock = 0
        self.runner_on_async_poll(host, result._result, jid, clock)

    def v2_runner_on_async_ok(self, result):
        self._log("v2_runner_on_async_ok(self, result)")
        host = result._host.get_name()
        jid = result._result.get('ansible_job_id')
        self.runner_on_async_ok(host, result._result, jid)

    def v2_runner_on_async_failed(self, result):
        self._log("v2_runner_on_async_failed(self, result)")
        host = result._host.get_name()
        jid = result._result.get('ansible_job_id')
        self.runner_on_async_failed(host, result._result, jid)

    #no v1 correspondance
    def v2_runner_on_file_diff(self, result, diff):
        self._log("v2_runner_on_file_diff(self, result, diff)")

    def v2_playbook_on_start(self, playbook):
        self._log("v2_playbook_on_start(self, playbook)")
        self.playbook_on_start()

    def v2_playbook_on_notify(self, result, handler):
        self._log("v2_playbook_on_notify(self, result, handler)")
        host = result._host.get_name()
        self.playbook_on_notify(host, handler)

    def v2_playbook_on_no_hosts_matched(self):
        self._log("v2_playbook_on_no_hosts_matched(self)")
        self.playbook_on_no_hosts_matched()

    def v2_playbook_on_no_hosts_remaining(self):
        self._log("v2_playbook_on_no_hosts_remaining(self)")
        self.playbook_on_no_hosts_remaining()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._log("v2_playbook_on_task_start(self, task, is_conditional)")
        self.playbook_on_task_start(task, is_conditional)

    #no v1 correspondance
    def v2_playbook_on_cleanup_task_start(self, task):
        self._log("v2_playbook_on_cleanup_task_start(self, task)")

    #no v1 correspondance
    def v2_playbook_on_handler_task_start(self, task):
        self._log("v2_playbook_on_handler_task_start(self, task)")


    def v2_playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        self._log("v2_playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None)")
        self.playbook_on_vars_prompt(varname, private, prompt, encrypt, confirm, salt_size, salt, default)

    def v2_playbook_on_setup(self):
        self._log("v2_playbook_on_setup(self)")
        self.playbook_on_setup()

    def v2_playbook_on_import_for_host(self, result, imported_file):
        self._log("v2_playbook_on_import_for_host(self, result, imported_file)")
        host = result._host.get_name()
        self.playbook_on_import_for_host(host, imported_file)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        self._log("v2_playbook_on_not_import_for_host(self, result, missing_file)")
        host = result._host.get_name()
        self.playbook_on_not_import_for_host(host, missing_file)

    def v2_playbook_on_play_start(self, play):
        self._log("v2_playbook_on_play_start(self, play)")

        #
        # TODO: play.roles contains the list of roles for this play, freshly loaded.  Cache here so we can use later
        #       Play obj: ansible/playbook/play.py
        #
        self._log("\tROLES: " + str(play.roles))
        self.playbook_on_play_start(play.name)

    def v2_playbook_on_stats(self, stats):
        self._log("v2_playbook_on_stats(self, stats)")
        self.playbook_on_stats(stats)

    def v2_on_file_diff(self, result):
        self._log("v2_on_file_diff(self, result)")
        if 'diff' in result._result:
            host = result._host.get_name()
            self.on_file_diff(host, result._result['diff'])

    #no v1 correspondance
    def v2_playbook_on_include(self, included_file):
        self._log("v2_playbook_on_include(self, included_file)")

    def v2_playbook_item_on_ok(self, result):
        self._log("v2_playbook_item_on_ok(self, result)")

    def v2_playbook_item_on_failed(self, result):
        self._log("v2_playbook_item_on_failed(self, result)")

    def v2_playbook_item_on_skipped(self, result):
        self._log("v2_playbook_item_on_skipped(self, result)")

    def v2_playbook_retry(self, result):
        self._log("v2_playbook_retry(self, result)")

