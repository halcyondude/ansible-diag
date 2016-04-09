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
module: debug_log_json
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
from collections import defaultdict
from datetime import datetime, timedelta
from ansible.plugins.callback import CallbackBase



class CallbackModule(CallbackBase):
    """
    This plugin generates diagnostics and analysis of playbook execution

    ansible-playbook invocation generally looks like...

    playbook_on_start()
    on_any()
    set_play_context()
    playbook_on_play_start()
    on_any

    FOR EACH TASK
    playbook_on_task_start()
    on_any()
    runner_on_[ failed | ok | skipped | unreachable | no_hosts | async_poll | async_ok | async_failed ]()
    on_any()
    END FOR

    This callback builds up an in-memory tree containing all of the tasks, and the associated result objects
    serialized as (useful) json.  It's done in a manner befitting a newbie to python. patches welcome :)

    As the end goal is a big JSON tree formatted a few ways for later use in other tooling, dicts with string keys
    are happily serializable objects.  Note: dicts with non-string keys are non-happy for json serialization.

    Formatted output for ansible-playbook runs (secondary) is also meant to be useful, but is switched off by default.

    There are a few different data sets generated.  The trees use a dict named "children" for sub-nodes.  The trees
    also contain at node level (sibling to the "children" collection if existing) a few rollups containing the sums
    for all children of:
     - total runtime (SUM(deltas))
     - ok/skip/changed counts
     - timespan covered by all children

    Reports Generated might include:
     - Flat CSV data (start, end, delta, runnercode, rolename, rolepath, taskname)
     - Tree (json): playbook \ host \ role-instance \ task
     - Playbook summary, containing tasks, includes, roles, etc using indenting and rollups.  The idea is to provide
       a textual overview showing (via indentation) what occured.
    """
    CALLBACK_VERSION = 1.9
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'debug_log_json'

    # note: does nothing in v2
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

    #
    # Helper funcs for logging
    #
    def _log(self, msg):
        self._display.display(msg)

    def _dlog(self, msg):
        return;
        # TODO: make this better, handle varargs
        # note: display(self, msg, color=None, stderr=False, screen_only=False, log_only=False)
        #self._display.display(msg)

    def _to_dir_s(self, thing):
        return pprint.pformat(dir(thing), indent=2)

    def _to_vars_s(self, thing):
        return pprint.pformat(vars(thing), indent=2)

    def _to_json_s(self, thing):
        return json.dumps(thing, sort_keys=True, indent=2, separators=(',', ': '))

    def _get_datetime(self, timestring):
        # 2016-03-27 00:58:07.323882 (so very close to ISO 8601, but not.)
        return datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S.%f")

    # BEGIN CLASS STATE

    # Used to hold current task
    _cur_task = None

    # hosts.  dict. key: hostname, value: tasklist (a list of tuples) 
    _hosts = defaultdict(list)

    # tasklist    = list of dicts ( tasktype, tasksubtype, name, result )

    # [0] entrytype    = Task (T).  Future: Play (P), Metadata (M), Whoknowswhatnext (?)
    # [1] runnercode  = failed, ok, skipped, unreachable, no_hosts, async_poll, async_ok, async_failed
    # [2] rolename    = role name
    # [3] rolepath    = role path (actual file)
    # [4] taskname    = name of the task
    # [5] result      = if ok, fail, unreachable: start/end/delta/stderr/stdout/etc.
    #                   if skiped: item
    # TODO: map out the rest for doc string
    def _handle_runner_callback(self, runnercode, host, result):
        start = self._get_datetime(result['start'])
        end =   self._get_datetime(result['end'])

        # 0:00:00.501769
        #delta =

        new_task = {'entrytype': 'TASK_RECORD',
                    'runnercode': runnercode,
                    'rolename':   self._cur_task._role._role_name,
                    'rolepath':   self._cur_task._role._role_path,
                    'taskname':   self._cur_task.name,
                    'result':     result,
                    'start':      start,
                    'end':        end}

        self._hosts[host].append(new_task)
        self._cur_task = None

    def _handle_runner_async_callback(self, runnercode, host, result, jobid):
        # TODO: handle async tasks
        return

    def playbook_on_stats(self, stats):
        self._dlog("playbook_on_stats( %s )" % str(stats))

        self._dlog("===================")
        self._dlog("FLAT DUMP (by host)")
        self._dlog("===================")

        for host,tasks in self._hosts.items():
            self._dlog("Host: " + host)

            # tasks is a list of task records (each one a dict).  The makes for easy json serialization, provided
            # keys are always strings (only)
            for t in tasks:
                #self._dlog(self._to_json_s(task))

                # TODO: delta is still just the string from results object (vs. deserialized timespan)
                r = t['result']
                msg = "{0}, {1}, {2}, {3}, {4}, {5}".format(
                    t['start'], t['end'], r['delta'], t['runnercode'], t['rolename'], t['taskname'])
                self._log(msg)

        # note: all trees start with [playbook \ host].

        # generate a list of tasks grouped by role invocation (instance of a role being called).
#        root = { 'name': 'Hosts', 'children': defaultdict(list)}
#        root_hosts_dict = root['children']
#
#        for host,tasks in self._hosts.items():
#            cur_host =      root_hosts_dict[host] = { 'name': host, 'role-invocations': defaultdict(list)}
#            cur_role_name = None

            #for t in tasks:






    def set_play_context(self, play_context):
        self._dlog("set_play_context(self, play_context)")

    def on_any(self, *args, **kwargs):
        self._dlog("on_any(self, *args, **kwargs)")
#        self._dlog("\ttype arg[0]: " + str(type(args[0])))
#        for arg in args:
#            self._dlog("\t(arg):" + str(arg) + " TYPE: " + str(type(arg)))

    # TODO: do we need to do anything with ignore_errors?
    def runner_on_failed(self, host, res, ignore_errors=False):
        self._dlog("runner_on_failed(self, host, res, ignore_errors=False)")
        self._handle_runner_callback("failed", host, res)

    def runner_on_ok(self, host, res):
        self._dlog("runner_on_ok()")
        self._handle_runner_callback("ok", host, res)

    def runner_on_skipped(self, host, item=None):
        self._dlog("runner_on_skipped(self, host, item=None)")

    def runner_on_unreachable(self, host, res):
        self._dlog("runner_on_unreachable(self, host, res)")
        self._handle_runner_callback("unreachable", host, res)

    def runner_on_no_hosts(self):
        self._dlog("runner_on_no_hosts(self)")

    def runner_on_async_poll(self, host, res, jid, clock):
        self._dlog("runner_on_async_poll(self, host, res, jid, clock)")

    def runner_on_async_ok(self, host, res, jid):
        self._dlog("runner_on_async_ok(self, host, res, jid)")
        self._handle_runner_async_callback("ok", host, res, jid)

    def runner_on_async_failed(self, host, res, jid):
        self._dlog("runner_on_async_failed(self, host, res, jid)")
        self._handle_runner_async_callback("failed", host, res, jid)

    def playbook_on_start(self):
        self._dlog("playbook_on_start(self)")

    def playbook_on_notify(self, host, handler):
        self._dlog("playbook_on_notify(self, host, handler)")

    def playbook_on_no_hosts_matched(self):
        self._dlog("playbook_on_no_hosts_matched(self)")

    def playbook_on_no_hosts_remaining(self):
        self._dlog("playbook_on_no_hosts_remaining(self)")

    # note: function sig in base class is a misnomer (name)
    def playbook_on_task_start(self, task, is_conditional):
        self._dlog("playbook_on_task_start( %s )" % str(task))
        self._cur_task = task

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        self._dlog("playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None)")

    def playbook_on_setup(self):
        self._dlog("playbook_on_setup(self)")

    def playbook_on_import_for_host(self, host, imported_file):
        self._dlog("playbook_on_import_for_host(self, host, imported_file)")

    def playbook_on_not_import_for_host(self, host, missing_file):
        self._dlog("playbook_on_not_import_for_host(self, host, missing_file)")

    def playbook_on_play_start(self, name):
        self._dlog("playbook_on_play_start( %s )" % str(name))

    def on_file_diff(self, host, diff):
        self._dlog("on_file_diff(self, host, diff)")

