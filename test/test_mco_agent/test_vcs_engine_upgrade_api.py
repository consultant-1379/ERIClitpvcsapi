import unittest
import mock
import os
import sys

sys.path.append('./puppet/mcollective_agents/files')

from vcs_engine_upgrade_api import (VcsEngineUpgradeApi,
                                    VcsEngineUpgradeException)


class TestVcsEngineUpgradeApi(unittest.TestCase):

    def setUp(self):
        self.api = VcsEngineUpgradeApi()

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_hagrp_display_all_frozen(self, mock_run):
        result = ("#Group           Attribute             System     Value\n"
                  "Grp_CS_c1_CS1    Frozen                global     0\n"
                  "Grp_CS_c1_CS2    Frozen                global     1")

        mock_run.return_value = 0, result, ''
        response = self.api.hagrp_display_all_frozen()

        mock_run.assert_called_once_with("hagrp -display -attribute Frozen")
        self.assertEqual(response['out'], result)

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_haconf_makerw(self, mock_run):
        mock_run.return_value = 0, '', ''

        request = {'haaction': 'makerw'}
        self.api.haconf(request)

        mock_run.assert_called_once_with("haconf -makerw")

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_haconf_makero(self, mock_run):
        mock_run.return_value = 0, '', ''

        request = {'haaction': 'makero'}
        self.api.haconf(request)

        mock_run.assert_called_once_with("haconf -dump -makero")

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_hagrp_freeze(self, mock_run):
        mock_run.return_value = 0, '', ''

        request = {'group_name': 'Grp_CS_c1_CS1'}
        self.api.hagrp_freeze(request)

        mock_run.assert_called_once_with(
            "hagrp -freeze Grp_CS_c1_CS1 -persistent")

    @mock.patch('vcs_node_upgrade_ordering_api.RPCAgent.run')
    def test_hagrp_unfreeze(self, mock_run):
        mock_run.return_value = 0, '', ''

        request = {'group_name': 'Grp_CS_c1_CS1'}
        self.api.hagrp_unfreeze(request)

        mock_run.assert_called_once_with(
            "hagrp -unfreeze Grp_CS_c1_CS1 -persistent")
