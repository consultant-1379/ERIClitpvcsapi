#!/bin/env python

'''
Request format:
{ "callerid": null,
  "agent": "vcs_engine_upgrade_api",
  "data":{"process_results":true},
  "uniqid":"e8937c54738d5cb09b3ca8d668d821ce",
  "sender":"ms1",
  "action":"pythontest"
}
'''

from vcs_node_upgrade_ordering_api import RPCAgent

import sys
import json
import os
import subprocess
from collections import namedtuple

VCS_GROUP_IS_FROZEN_ERR = "VCS WARNING V-16-1-40209 Group is already persistently frozen"
VCS_GROUP_IS_UNFROZEN_ERR = "VCS WARNING V-16-1-40202 Group is not persistently frozen"
VCS_ALREADY_WRITABLE = 'VCS WARNING V-16-1-10364 Cluster already writable.'


class VcsEngineUpgradeException(Exception):
    pass


class VcsEngineUpgradeApi(RPCAgent):

    def run_vcs_command(self, command, expected_errors=[],
                        rewrite_retcode=False):
        c, o, e = self.run(command)
        if c:
            for expected_error in expected_errors:
                if expected_error in e:
                    if rewrite_retcode:
                        c = 0
                    return c, o, e
            raise VcsEngineUpgradeException(
                "Error running '{0}': Out: '{1}' Err: '{2}'".format(
                    command, o, e))
        return c, o, e

    def hagrp_display_all_frozen(self):
        cmd = "hagrp -display -attribute Frozen"
        c, o, e = self.run_vcs_command(cmd)
        return {"retcode": c, "out": o, "err": e}

    def haconf(self, request):
        cmd = ""

        valid_actions = ["makerw", "makero"]

        if request["haaction"] not in valid_actions:
            err_msg = ("Failure to execute command mco rpc "
                       "vcs_engine_upgrade_api haconf, Reason: Invalid "
                       "action supplied - {0}").format(request["haaction"])
            raise VcsEngineUpgradeException(err_msg)

        if request["haaction"] == "makerw":
            cmd = "haconf -{0}".format(request["haaction"])
            allowed_errs = [VCS_ALREADY_WRITABLE]
            rewrite = True
        else:
            cmd = "haconf -dump -{0}".format(request["haaction"])
            allowed_errs = []
            rewrite = False

        c, o, e = self.run_vcs_command(cmd,
                                       expected_errors=allowed_errs,
                                       rewrite_retcode=rewrite)
        return {"retcode": c, "out": o, "err": e}

    def hagrp_freeze(self, request):
        group = request['group_name']
        cmd = "hagrp -freeze {0} -persistent".format(group)
        expected_errors = []
        expected_errors.append(VCS_GROUP_IS_FROZEN_ERR)
        expected_errors.append(VCS_GROUP_IS_UNFROZEN_ERR)
        c, o, e = self.run_vcs_command(cmd, expected_errors)
        return {"retcode": c, "out": o, "err": e}

    def hagrp_unfreeze(self, request):
        group = request['group_name']
        cmd = "hagrp -unfreeze {0} -persistent".format(group)
        c, o, e = self.run_vcs_command(cmd)
        return {"retcode": c, "out": o, "err": e}

    def get_package_file_info(self, request):
        package = request['package']
        cmd = "rpm -ql {0}".format(package)
        c, o, e = self.run_vcs_command(cmd)
        return {"retcode": c, "out": o, "err": e}

if __name__ == '__main__':
    VcsEngineUpgradeApi().action()
