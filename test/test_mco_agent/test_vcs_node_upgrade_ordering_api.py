import unittest
import mock
import os
import sys

sys.path.append('./puppet/mcollective_agents/files')

from vcs_node_upgrade_ordering_api import (VcsNodeUpgradeOrderingApi,
                                           RPCAgent,
                                           VCSNodeUpgradeOrderingException)


class TestRPCAgent(unittest.TestCase):

    def setUp(self):
        self.agent = RPCAgent()

    @mock.patch('vcs_node_upgrade_ordering_api.subprocess')
    def test_rpcagent_run(self, sub_proc):
        sub_proc.Popen = mock.Mock()
        communicate = mock.Mock(return_value=("expected out",
                                              "expected err"))
        process = mock.Mock(returncode=0,
                            communicate=communicate)
        sub_proc.Popen.return_value = process
        code, out, err = self.agent.run("ls")
        self.assertEqual(code, 0)
        self.assertEqual(out, "expected out")
        self.assertEqual(err, "expected err")

    @mock.patch('vcs_node_upgrade_ordering_api.sys')
    @mock.patch('vcs_node_upgrade_ordering_api.json')
    @mock.patch('__builtin__.open')
    def test_rpcagent_action(self, mock_open, mock_json, mock_sys):
        os.environ["MCOLLECTIVE_REQUEST_FILE"] = "/tmp/request"
        os.environ["MCOLLECTIVE_REPLY_FILE"] = "/tmp/reply"

        infile = mock.MagicMock()
        outfile = mock.MagicMock()

        requests_data = {"data1": {"process_res": "T",
                                     "my_data": "my_data1"},
                         "data2": {"process_res": "T"}}
        for req in requests_data:
            mock_json.load.return_value = {
                "action": "my_action",
                "data": requests_data[req],
            }

            action_response = "action response"
            self.agent.my_action = mock.Mock(return_value=action_response)

            mock_open.__enter__.side_effect = [infile, outfile]

            self.agent.action()

            mock_open.assert_any_call('/tmp/request', 'r')
            mock_open.assert_any_call('/tmp/reply', 'w')

            infile.assert_called_once()
            outfile.assert_called_once()

            mock_json.load.assert_any_call(
                mock_open().__enter__())
            mock_json.dump.assert_any_call(
                "action response", mock_open().__enter__())
            mock_open().__exit__.assert_called_with(None, None, None)
            mock_sys.assert_has_calls([mock.call.exit(0)])


class TestVcsNodeUpgradeOrderingApi(unittest.TestCase):

    def setUp(self):
        self.api = VcsNodeUpgradeOrderingApi()

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_api_run_vcs_command(self, mock_run):
        mock_run.return_value = 0, "output", ""
        c, o, e = self.api.run_vcs_command("ls")
        mock_run.assert_called_once_with("ls")
        self.assertEqual(c, 0)
        self.assertEqual(o, "output")
        self.assertEqual(e, "")

        mock_run.return_value = 1, "", "error"
        self.assertRaises(VCSNodeUpgradeOrderingException, self.api.run_vcs_command, "ls")

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_api_hagrp_state(self, mock_run):
        result = 'OFFLINE'
        mock_run.return_value = 0, result, ''

        request = {'group_name': 'Grp_CS_c1_CS1', 'sys': 'node1'}
        response = self.api.hagrp_state(request)

        mock_run.assert_called_once_with("hagrp -state Grp_CS_c1_CS1 -sys node1")
        self.assertEqual(response['out'], result)

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_api_hagrp_display_frozen(self, mock_run):
        result = "#Group           Attribute             System     Value\n" \
            "Grp_CS_c1_CS1    Frozen                global     0"

        mock_run.return_value = 0, result, ''

        request = {'group_name': 'Grp_CS_c1_CS1'}
        response = self.api.hagrp_display_frozen(request)

        mock_run.assert_called_once_with(
            "hagrp -display Grp_CS_c1_CS1 -attribute Frozen")
        self.assertEqual(response['out'], False)

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_api_causal_cluster_overview(self, mock_run):
        result = '[]'
        mock_run.return_value = 0, result, ''

        response = self.api.causal_cluster_overview()

        mock_run.assert_called_once_with("/opt/ericsson/neo4j/scripts/cluster_overview.py json")
        self.assertEqual(response['out'], result)
