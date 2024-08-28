#!/bin/env python

'''
Results and Exceptions
0   OK
1   OK, failed. All the data parsed ok, we have a action matching the request
    but the requested action could not be completed.  RPCAborted
2   Unknown action  UnknownRPCAction
3   Missing data    MissingRPCData
4   Invalid data    InvalidRPCData
5   Other error     UnknownRPCError

Request format:
{ "callerid": null,
  "agent": "vcs_node_upgrade_ordering_api",
  "data":{"process_results":true},
  "uniqid":"e8937c54738d5cb09b3ca8d668d821ce",
  "sender":"ms1",
  "action":"pythontest"
}
'''

import sys
import json
import os
import subprocess
from collections import namedtuple

MCOLLECTIVE_REPLY_FILE = "MCOLLECTIVE_REPLY_FILE"
MCOLLECTIVE_REQUEST_FILE = "MCOLLECTIVE_REQUEST_FILE"

OK = 0
RPCAborted = 1
UnknownRPCAction = 2
MissingRPCData = 3
InvalidRPCData = 4
UnknownRPCError = 5


class VCSNodeUpgradeOrderingException(Exception):
    pass


class RPCAgent(object):

    def action(self):
        exit_value = OK
        with open(os.environ[MCOLLECTIVE_REQUEST_FILE], 'r') as infile:
            request = json.load(infile)

        action = request["action"]
        method = getattr(self, action, None)
        if callable(method):
            if len(request['data']) > 1:
                reply = method(request['data'])
            else:
                reply = method()
        else:
            reply = {}
            exit_value = UnknownRPCAction

        with open(os.environ[MCOLLECTIVE_REPLY_FILE], 'w') as outfile:
            json.dump(reply, outfile)

        sys.exit(exit_value)

    @staticmethod
    def run(command):
        env = dict(os.environ)
        env['PATH'] = "/opt/VRTSvcs/bin:{0}".format(env['PATH'])
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True,
                             env=env)
        out, err = p.communicate()
        return p.returncode, out.strip(), err.strip()


class VcsNodeUpgradeOrderingApi(RPCAgent):

    def run_vcs_command(self, command, expected_errors=[],
                        rewrite_retcode=False):
        c, o, e = self.run(command)
        if c:
            for expected_error in expected_errors:
                if expected_error in e:
                    if rewrite_retcode:
                        c = 0
                    return c, o, e
            raise VCSNodeUpgradeOrderingException(
                "Error running '{0}': Out: '{1}' Err: '{2}'".format(
                    command, o, e))
        return c, o, e

    def hagrp_state(self, request):
        cmd = "hagrp -state {group_name} -sys {sys}".format(**request)
        c, o, e = self.run_vcs_command(cmd)
        return {"retcode": c, "out": o, "err": e}

    def hagrp_display_frozen(self, request):
        group = request['group_name']
        cmd = "hagrp -display {0} -attribute Frozen".format(group)
        c, o, e = self.run_vcs_command(cmd)

        if o:
            lines = o.splitlines()[1:]

            frozen = lines[0].split()[3]

            if "1" == frozen:
                o = True
            else:
                o = False
        return {"retcode": c, "out": o, "err": e}

    def causal_cluster_overview(self):
        cmd = "/opt/ericsson/neo4j/scripts/cluster_overview.py json"
        c, o, e = self.run_vcs_command(cmd)
        return {"retcode": c, "out": o, "err": e}

if __name__ == '__main__':
    VcsNodeUpgradeOrderingApi().action()
