##############################################################################
# COPYRIGHT Ericsson AB 2014
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################
import unittest

import mock
import re

from litp.core.validators import ValidationError
from litp.core.exceptions import ViewError

from vcs_extension.vcs_extension import (VcsExtension,
                                         VcsClusterValidator,
                                         VcsClusterHaManagerValidator,
                                         VcsCSDependencyListValidator,
                                         VcsCSInitialOnlineDependencyListValidator,
                                         VCSTriggerTypeValidator,
                                         condense_name)

FFL_OVERVIEW_JSON = [{"addresses": {"http": "10.247.246.10:7474",
                       "bolt": "10.247.246.10:7687",
                       "https": "10.247.246.10:7473"},
         "databases": {"dps": "FOLLOWER",
                       "system": "FOLLOWER"},
         "database": "default", "cypher_available": 1,
         "host": {"ip": "10.247.246.10", "hostname": "node2",
                  "aliases": ["db-2"]}, "version": "3.5.3",
         "role": "FOLLOWER", "groups": [],
         "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
            "addresses": {"http": "10.247.246.16:7474",
                          "bolt": "10.247.246.16:7687",
                          "https": "10.247.246.16:7473"},
            "databases": {"dps": "FOLLOWER",
                          "system": "LEADER"},
            "database": "default", "cypher_available": 0,
            "host": {"ip": "10.247.246.16", "hostname": "node3",
                     "aliases": ["db-3"]}, "version": "3.5.3",
            "role": "FOLLOWER", "groups": [],
            "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
            "addresses": {"http": "10.247.246.17:7474",
                          "bolt": "10.247.246.17:7687",
                          "https": "10.247.246.17:7473"},
            "database": "default", "cypher_available": 1,
            "databases": {"dps": "LEADER",
                          "system": "FOLLOWER"},
            "host": {"ip": "10.247.246.17", "hostname": "node1",
                     "aliases": ["db-1"]}, "version": "3.5.3",
            "role": "LEADER", "groups": [],
            "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_BAD_HOSTNAME = [{"addresses": {"http": "10.247.246.10:7474",
                       "bolt": "10.247.246.10:7687",
                       "https": "10.247.246.10:7473"},
         "databases": {"dps": "FOLLOWER",
                       "system": "FOLLOWER"},
         "database": "default", "cypher_available": 1,
         "host": {"ip": "10.247.246.10", "hostname": "bad_nde2",
                  "aliases": ["db-2"]}, "version": "3.5.3",
         "role": "FOLLOWER", "groups": [],
         "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
            "addresses": {"http": "10.247.246.16:7474",
                          "bolt": "10.247.246.16:7687",
                          "https": "10.247.246.16:7473"},
            "databases": {"dps": "FOLLOWER",
                          "system": "LEADER"},
            "database": "default", "cypher_available": 0,
            "host": {"ip": "10.247.246.16", "hostname": "bad_nde3",
                     "aliases": ["db-3"]}, "version": "3.5.3",
            "role": "FOLLOWER", "groups": [],
            "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
            "addresses": {"http": "10.247.246.17:7474",
                          "bolt": "10.247.246.17:7687",
                          "https": "10.247.246.17:7473"},
            "database": "default", "cypher_available": 1,
            "databases": {"dps": "LEADER",
                          "system": "FOLLOWER"},
            "host": {"ip": "10.247.246.17", "hostname": "bad_nde1",
                     "aliases": ["db-1"]}, "version": "3.5.3",
            "role": "LEADER", "groups": [],
            "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_NO_HOSTNAME = [{"addresses": {"http": "10.247.246.10:7474",
                                   "bolt": "10.247.246.10:7687",
                                   "https": "10.247.246.10:7473"},
                     "databases": {"dps": "FOLLOWER",
                                   "system": "FOLLOWER"},
                     "database": "default", "cypher_available": 1,
                     "host": {"ip": "10.247.246.10",
                              "aliases": ["db-2"]}, "version": "3.5.3",
                     "role": "FOLLOWER", "groups": [],
                     "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                        "addresses": {"http": "10.247.246.16:7474",
                                      "bolt": "10.247.246.16:7687",
                                      "https": "10.247.246.16:7473"},
                        "databases": {"dps": "FOLLOWER",
                                      "system": "FOLLOWER"},
                        "database": "default", "cypher_available": 0,
                        "host": {"ip": "10.247.246.16",
                                 "aliases": ["db-3"]}, "version": "3.5.3",
                        "role": "LEADER", "groups": [],
                        "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                        "addresses": {"http": "10.247.246.17:7474",
                                      "bolt": "10.247.246.17:7687",
                                      "https": "10.247.246.17:7473"},
                        "databases": {"dps": "FOLLOWER",
                                      "system": "LEADER"},
                        "database": "default", "cypher_available": 1,
                        "host": {"ip": "10.247.246.17",
                                 "aliases": ["db-1"]}, "version": "3.5.3",
                        "role": "FOLLOWER", "groups": [],
                        "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_NO_DPS = [{"addresses": {"http": "10.247.246.10:7474",
                               "bolt": "10.247.246.10:7687",
                               "https": "10.247.246.10:7473"},
                 "databases": {"dps": "FOLLOWER",
                               "system": "FOLLOWER"},
                 "database": "default", "cypher_available": 1,
                 "host": {"ip": "10.247.246.10", "hostname": "node2",
                          "aliases": ["db-2"]}, "version": "3.5.3",
                 "role": "FOLLOWER", "groups": [],
                 "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                    "addresses": {"http": "10.247.246.16:7474",
                                  "bolt": "10.247.246.16:7687",
                                  "https": "10.247.246.16:7473"},
                    "databases": {"dps": "FOLLOWER",
                                  "system": "FOLLOWER"},
                    "database": "default", "cypher_available": 0,
                    "host": {"ip": "10.247.246.16", "hostname": "node3",
                             "aliases": ["db-3"]}, "version": "3.5.3",
                    "role": "FOLLOWER", "groups": [],
                    "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                    "addresses": {"http": "10.247.246.17:7474",
                                  "bolt": "10.247.246.17:7687",
                                  "https": "10.247.246.17:7473"},
                    "databases": {"dps": "FOLLOWER",
                                  "system": "LEADER"},
                    "database": "default", "cypher_available": 1,
                    "host": {"ip": "10.247.246.17", "hostname": "node1",
                             "aliases": ["db-1"]}, "version": "3.5.3",
                    "role": "FOLLOWER", "groups": [],
                    "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_NO_DPS_KEY = [{"addresses": {"http": "10.247.246.10:7474",
                               "bolt": "10.247.246.10:7687",
                               "https": "10.247.246.10:7473"},
                 "databases": {"blah": "FOLLOWER",
                               "system": "FOLLOWER"},
                 "database": "default", "cypher_available": 1,
                 "host": {"ip": "10.247.246.10", "hostname": "node2",
                          "aliases": ["db-2"]}, "version": "3.5.3",
                 "role": "FOLLOWER", "groups": [],
                 "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                    "addresses": {"http": "10.247.246.16:7474",
                                  "bolt": "10.247.246.16:7687",
                                  "https": "10.247.246.16:7473"},
                    "databases": {"blah": "FOLLOWER",
                                  "system": "FOLLOWER"},
                    "database": "default", "cypher_available": 0,
                    "host": {"ip": "10.247.246.16", "hostname": "node3",
                             "aliases": ["db-3"]}, "version": "3.5.3",
                    "role": "FOLLOWER", "groups": [],
                    "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                    "addresses": {"http": "10.247.246.17:7474",
                                  "bolt": "10.247.246.17:7687",
                                  "https": "10.247.246.17:7473"},
                    "databases": {"blah": "FOLLOWER",
                                  "system": "LEADER"},
                    "database": "default", "cypher_available": 1,
                    "host": {"ip": "10.247.246.17", "hostname": "node1",
                             "aliases": ["db-1"]}, "version": "3.5.3",
                    "role": "FOLLOWER", "groups": [],
                    "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_NO_SYSTEM = [{"addresses": {"http": "10.247.246.10:7474",
                                   "bolt": "10.247.246.10:7687",
                                   "https": "10.247.246.10:7473"},
                     "databases": {"dps": "FOLLOWER",
                                   "system": "FOLLOWER"},
                     "database": "default", "cypher_available": 1,
                     "host": {"ip": "10.247.246.10", "hostname": "node2",
                              "aliases": ["db-2"]}, "version": "3.5.3",
                     "role": "FOLLOWER", "groups": [],
                     "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                        "addresses": {"http": "10.247.246.16:7474",
                                      "bolt": "10.247.246.16:7687",
                                      "https": "10.247.246.16:7473"},
                        "databases": {"dps": "FOLLOWER",
                                      "system": "FOLLOWER"},
                        "database": "default", "cypher_available": 0,
                        "host": {"ip": "10.247.246.16", "hostname": "node3",
                                 "aliases": ["db-3"]}, "version": "3.5.3",
                        "role": "LEADER", "groups": [],
                        "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                        "addresses": {"http": "10.247.246.17:7474",
                                      "bolt": "10.247.246.17:7687",
                                      "https": "10.247.246.17:7473"},
                        "databases": {"dps": "FOLLOWER",
                                      "system": "FOLLOWER"},
                        "database": "default", "cypher_available": 1,
                        "host": {"ip": "10.247.246.17", "hostname": "node1",
                                 "aliases": ["db-1"]}, "version": "3.5.3",
                        "role": "FOLLOWER", "groups": [],
                        "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_TWO_SYSTEM = [{"addresses": {"http": "10.247.246.10:7474",
                                   "bolt": "10.247.246.10:7687",
                                   "https": "10.247.246.10:7473"},
                     "databases": {"dps": "FOLLOWER",
                                   "system": "FOLLOWER"},
                     "database": "default", "cypher_available": 1,
                     "host": {"ip": "10.247.246.10", "hostname": "node2",
                              "aliases": ["db-2"]}, "version": "3.5.3",
                     "role": "FOLLOWER", "groups": [],
                     "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                        "addresses": {"http": "10.247.246.16:7474",
                                      "bolt": "10.247.246.16:7687",
                                      "https": "10.247.246.16:7473"},
                        "databases": {"dps": "LEADER",
                                      "system": "LEADER"},
                        "database": "default", "cypher_available": 0,
                        "host": {"ip": "10.247.246.16", "hostname": "node3",
                                 "aliases": ["db-3"]}, "version": "3.5.3",
                        "role": "LEADER", "groups": [],
                        "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                        "addresses": {"http": "10.247.246.17:7474",
                                      "bolt": "10.247.246.17:7687",
                                      "https": "10.247.246.17:7473"},
                        "databases": {"dps": "FOLLOWER",
                                      "system": "LEADER"},
                        "database": "default", "cypher_available": 1,
                        "host": {"ip": "10.247.246.17", "hostname": "node1",
                                 "aliases": ["db-1"]}, "version": "3.5.3",
                        "role": "FOLLOWER", "groups": [],
                        "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]

FFL_OVERVIEW_NO_SYSTEM_KEY = [{"addresses": {"http": "10.247.246.10:7474",
                               "bolt": "10.247.246.10:7687",
                               "https": "10.247.246.10:7473"},
                 "databases": {"dps": "FOLLOWER",
                               "blah": "FOLLOWER"},
                 "database": "default", "cypher_available": 1,
                 "host": {"ip": "10.247.246.10", "hostname": "node2",
                          "aliases": ["db-2"]}, "version": "3.5.3",
                 "role": "FOLLOWER", "groups": [],
                 "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {
                    "addresses": {"http": "10.247.246.16:7474",
                                  "bolt": "10.247.246.16:7687",
                                  "https": "10.247.246.16:7473"},
                    "databases": {"dps": "FOLLOWER",
                                  "blah": "FOLLOWER"},
                    "database": "default", "cypher_available": 0,
                    "host": {"ip": "10.247.246.16", "hostname": "node3",
                             "aliases": ["db-3"]}, "version": "3.5.3",
                    "role": "LEADER", "groups": [],
                    "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {
                    "addresses": {"http": "10.247.246.17:7474",
                                  "bolt": "10.247.246.17:7687",
                                  "https": "10.247.246.17:7473"},
                    "databases": {"dps": "FOLLOWER",
                                  "blah": "FOLLOWER"},
                    "database": "default", "cypher_available": 1,
                    "host": {"ip": "10.247.246.17", "hostname": "node1",
                             "aliases": ["db-1"]}, "version": "3.5.3",
                    "role": "FOLLOWER", "groups": [],
                    "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}]


class TestVcsExtension(unittest.TestCase):

    def setUp(self):
        self.ext = VcsExtension()

    def test_property_types_registered(self):
        # Assert that only extension's property types
        # are defined.
        prop_types_expected = ['cluster_type', 'vcs_cluster_id', 'net_names',
                               'default_nic_mon_type',
                               'cs_initial_online_type',
                               'app_agent_num_threads',
                               'vcs_seed_threshold']
        prop_types = [pt.property_type_id for pt in
                      self.ext.define_property_types()]
        self.assertEquals(prop_types_expected, prop_types)

    def test_item_types_registered(self):
        # Assert that only extension's item types
        # are defined.
        item_types_expected = ['vcs-cluster', 'vcs-clustered-service',
                               'vcs-network-host', 'vcs-trigger']
        item_types = [it.item_type_id for it in
                      self.ext.define_item_types()]
        self.assertEquals(item_types_expected, item_types)

    def test_validator_llt_low_prio_equal_llt_link(self):
        properties = {'llt_nets': 'hb1,hb2', "low_prio_net": "hb1"}
        errors = VcsClusterValidator().validate(properties)
        self.assertEquals(
            "<llt_nets - ValidationError - Cannot create more than one link for each network>",
            str(errors))

    def test_validator_llt_nets_more_than_seven(self):
        properties = {'llt_nets': 'hb1,hb2,hb3,hb4,hb5,hb6,hb7,hb8',
                      "low_prio_net": "hb11"}
        errors = VcsClusterValidator().validate(properties)
        self.assertEquals(
            '<llt_nets - ValidationError - Cannot set more than 7 links for LLT>',
            str(errors))

    def test_validator_validate(self):
        properties = {'llt_nets': 'hb1,hb2,hb3,hb4,hb5,hb6,hb7',
                      "low_prio_net": "hb11"}
        errors = VcsClusterValidator().validate(properties)
        self.assertEquals('None', str(errors))

    def test_validator_low_prio_has_commas(self):
        properties = {'llt_nets': 'hb1,hb2', "low_prio_net": "hb11,hb12"}
        errors = VcsClusterValidator().validate(properties)
        self.assertEquals(
            '<low_prio_net - ValidationError - Low priority link for LLT should not be a list>',
            str(errors))

    def test_validator_llt_duplicates(self):
        properties = {'llt_nets': 'hb1,hb1', "low_prio_net": "hb11"}
        errors = VcsClusterValidator().validate(properties)
        self.assertEquals(
            "<llt_nets - ValidationError - Cannot create more than one link for each network>",
            str(errors))

    def test_validator_dependency_list_success(self):
        properties = {'dependency_list': 'cs1,cs2'}
        errors = VcsCSDependencyListValidator().validate(properties)
        self.assertEquals('None', str(errors))

    def test_validator_dependency_list_blank_string(self):
        properties = {'dependency_list': ''}
        errors = VcsCSDependencyListValidator().validate(properties)
        self.assertEquals('None', str(errors))

    def test_validator_dependency_list_none(self):
        properties = {}
        errors = VcsCSDependencyListValidator().validate(properties)
        self.assertEquals('None', str(errors))

    def test_validator_dependency_list_duplicates(self):
        properties = {'dependency_list': 'cs1,cs1,cs2,cs2'}
        errors = VcsCSDependencyListValidator().validate(properties)
        self.assertEquals(
            '<dependency_list - ValidationError - The following vcs-clustered-services have been specified more than once: cs1, cs2.>',
            str(errors))

    def test_validator_dependency_list_exceeds_error(self):
        properties = {
            'dependency_list': 'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39'}
        errors = VcsCSDependencyListValidator().validate(properties)
        self.assertEquals(
            '<dependency_list - ValidationError - There are "65" dependencies specified. The maximum number of dependencies supported is "64".>',
            str(errors))

        # Validate initial_online_dependency_list

    def test_validator_init_online_dependency_list_success(self):
        properties = {'initial_online_dependency_list': 'cs1,cs2'}
        errors = VcsCSInitialOnlineDependencyListValidator().validate(
            properties)
        self.assertEquals('None', str(errors))

    def test_validator_init_online_dependency_list_blank_string(self):
        properties = {'initial_online_dependency_list': ''}
        errors = VcsCSInitialOnlineDependencyListValidator().validate(
            properties)
        self.assertEquals('None', str(errors))

    def test_validator_init_online_dependency_list_none(self):
        properties = {}
        errors = VcsCSInitialOnlineDependencyListValidator().validate(
            properties)
        self.assertEquals('None', str(errors))

    def test_validator_init_online_dependency_list_duplicates(self):
        properties = {'initial_online_dependency_list': 'cs1,cs1,cs2,cs2'}
        errors = VcsCSInitialOnlineDependencyListValidator().validate(
            properties)
        self.assertEquals(
            '<initial_online_dependency_list - ValidationError - The following vcs-clustered-services have been specified more than once: cs1, cs2.>',
            str(errors))

    def test_validator_init_online_dependency_list_exceeds_error(self):
        properties = {
            'initial_online_dependency_list': 'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39'}
        errors = VcsCSInitialOnlineDependencyListValidator().validate(
            properties)
        self.assertEquals(
            '<initial_online_dependency_list - ValidationError - There are "65" dependencies specified. The maximum number of dependencies supported is "64".>',
            str(errors))

    def test_ha_manager_validator(self):
        validator = VcsClusterHaManagerValidator().validate
        properties = {'ha_manager': 'vcs'}
        self.assertEquals(None, validator(properties))
        properties = {'ha_manager': ''}
        self.assertEquals(None, validator(properties))
        properties = {'ha_manager': 'foobar'}
        self.assertTrue(isinstance(validator(properties), ValidationError))
        properties = {'ha_manager': None}
        self.assertTrue(isinstance(validator(properties), ValidationError))

    @mock.patch('vcs_extension.vcs_extension.PropertyType')
    def test_cluster_type_regex(self, property_type_patch):
        regex = r"^(vcs|sfha)$"
        re_compiled = re.compile(regex)

        self.assertEquals(None, re_compiled.search(unicode("vca")))
        self.assertNotEquals(None, re_compiled.search(unicode("vcs")))
        self.assertNotEquals(None, re_compiled.search(unicode("sfha")))
        self.assertEquals(None, re_compiled.search(unicode("c")))

        VcsExtension().define_property_types()

    @mock.patch('vcs_extension.vcs_extension.PropertyType')
    def test_cs_initial_online_type_regex(self, property_type_patch):
        regex = r"^(off|on)$"
        re_compiled = re.compile(regex)

        # Good scenarios
        self.assertNotEquals(None, re_compiled.search(unicode("off")))
        self.assertNotEquals(None, re_compiled.search(unicode("on")))
        # Bad Scenrios
        self.assertEquals(None, re_compiled.search(unicode("OFF")))
        self.assertEquals(None, re_compiled.search(unicode("ON")))
        self.assertEquals(None, re_compiled.search(unicode("off|on")))
        self.assertEquals(None, re_compiled.search(unicode("son")))
        self.assertEquals(None, re_compiled.search(unicode("ons")))
        self.assertEquals(None, re_compiled.search(unicode("soff")))
        self.assertEquals(None, re_compiled.search(unicode("offs")))
        VcsExtension().define_property_types()

    def test_trigger_type_validator(self):
        properties = {'trigger_type': 'blah'}
        errors = VCSTriggerTypeValidator().validate(properties)
        self.assertEquals(
            '<trigger_type - ValidationError - Only "nofailover" and "postonline" trigger types currently supported.>',
            str(errors))

    def test_get_critical_cs_normal(self):
        cs = mock.Mock(item_id='CS1')
        cluster = mock.Mock(is_updated=lambda: False)
        cluster.query.return_value = [cs]
        ret = self.ext._get_critical_cs(cluster)
        self.assertEquals(ret, cs)

    def test_get_critical_cs_not_updated(self):
        # cluster updated but critical service not updated
        cs = mock.Mock(item_id='CS2')
        cluster = mock.Mock(is_updated=lambda: True,
                            critical_service=cs.item_id,
                            applied_properties={
                                'critical_service': cs.item_id})
        cluster.query.return_value = [cs]
        ret = self.ext._get_critical_cs(cluster)
        self.assertEquals(ret, cs)

    def test_get_critical_cs_updated(self):
        # critical service update but not for a deactivation
        cs = mock.Mock(item_id='CS2', deactivates=None)
        app_cs = mock.Mock(item_id='CS1')
        cluster = mock.Mock(is_updated=lambda: True,
                            critical_service=cs.item_id,
                            applied_properties={
                                'critical_service': app_cs.item_id})
        cluster.query.return_value = [cs]
        ret = self.ext._get_critical_cs(cluster)
        self.assertEquals(ret, cs)

    def test_get_critical_cs_deactivation(self):
        cs = mock.Mock(item_id='CS2', deactivates='CS1')
        app_cs = mock.Mock(item_id='CS1')
        cluster = mock.Mock(is_updated=lambda: True,
                            critical_service=cs.item_id,
                            applied_properties={
                                'critical_service': app_cs.item_id})
        cluster.query.side_effect = [[cs], [app_cs]]

        ret = self.ext._get_critical_cs(cluster)
        self.assertEquals(ret, app_cs)

    def test_get_critical_cs_post_deactivation(self):
        cs = mock.Mock(item_id='CS2', deactivates='CS1')
        app_cs = mock.Mock(item_id='CS1')
        cluster = mock.Mock(is_updated=lambda: True,
                            critical_service=cs.item_id,
                            applied_properties={
                                'critical_service': app_cs.item_id})
        cluster.query.side_effect = [[cs], [cs]]

        ret = self.ext._get_critical_cs(cluster)
        self.assertEquals(ret, cs)


class TestGetNodeOrderingView(unittest.TestCase):

    def setUp(self):
        self.ext = VcsExtension()
        self.result = {
            'node1': {'data': {}},
            'node2': {'data': {}}
        }
        self.plugin_api_context = mock.Mock()
        self.cluster = mock.Mock(critical_service='MockService', item_id='foo',
                                 vpath='/foo/foo')
        self.n1 = mock.Mock(item_id='n1', hostname='node1')
        self.n2 = mock.Mock(item_id='n2', hostname='node2')
        self.n3 = mock.Mock(item_id='n3', hostname='node3')
        self.n4 = mock.Mock(item_id='n4', hostname='node4')
        self.priority_service = mock.Mock(nodes=[self.n1, self.n2])
        self.priority_service.is_initial.return_value = False
        self.priority_service.is_for_removal.return_value = False

        def side_effect(*args, **kwargs):
            if args[0] == 'vcs-clustered-service' and \
                    kwargs['item_id'] != "sg_neo4j_clustered_service":
                 return [self.priority_service]
            elif args[0] == 'node' and kwargs['hostname'] == 'node1':
                return [self.n1]
            elif args[0] == 'node' and kwargs['hostname'] == 'node2':
                return [self.n2]

        self.cluster.query.side_effect = side_effect
        self.cluster.nodes = [self.n2, self.n1]
        self.priority_service.nodes = [self.n2, self.n1]
        self.plugin_api_context.rpc_command.return_value = self.result

    def test_no_service(self):
        self.cluster.critical_service = None
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals([], nodes)

    def test_rpc_failing(self):
        self.result['node1']['data']['out'] = None
        self.assertRaises(ViewError, self.ext.get_node_upgrade_ordering,
                          self.plugin_api_context, self.cluster)

    def test_rpc_no_results(self):
        self.assertRaises(ViewError, self.ext.get_node_upgrade_ordering,
                          self.plugin_api_context, self.cluster)

    def test_ordering_n1_n2(self):
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'ONLINE'
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals(['n1', 'n2'], nodes)

    def test_ordering_n2_n1(self):
        self.result['node1']['data']['out'] = 'ONLINE'
        self.result['node2']['data']['out'] = 'OFFLINE'
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals(['n2', 'n1'], nodes)

    def test_both_online(self):
        self.result['node1']['data']['out'] = 'ONLINE'
        self.result['node2']['data']['out'] = 'ONLINE'
        self.assertRaises(ViewError, self.ext.get_node_upgrade_ordering,
                          self.plugin_api_context, self.cluster)

    def test_both_offline(self):
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'OFFLINE'
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals(['n2', 'n1'], nodes)

    def test_4_node_cluster_order_n2_n1(self):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.result['node1']['data']['out'] = 'ONLINE'
        self.result['node2']['data']['out'] = 'OFFLINE'
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals(['n2', 'n1', 'n3', 'n4'], nodes)

    def test_4_node_cluster_order_n1_n2(self):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'ONLINE'
        nodes = self.ext.get_node_upgrade_ordering(self.plugin_api_context,
                                                   self.cluster)
        self.assertEquals(['n1', 'n2', 'n3', 'n4'], nodes)

    @mock.patch('vcs_extension.vcs_extension.VcsExtension._get_critical_cs')
    def test_get_critical_service_ordering_pos(self, mock_get_cs):
        mock_get_cs.return_value = self.priority_service
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'ONLINE'

        result = self.ext.get_critical_service_ordering(self.plugin_api_context, self.cluster)

        self.assertEqual(result, ['n1', 'n2'])

    def test_get_critical_service_ordering_is_initial(self):
        self.priority_service.is_initial.return_value = True

        result = self.ext.get_critical_service_ordering(self.plugin_api_context, self.cluster)

        self.assertEqual(result, [])

    def test_get_critical_service_ordering_is_for_removal(self):
        self.priority_service.is_for_removal.return_value = True

        result = self.ext.get_critical_service_ordering(self.plugin_api_context, self.cluster)

        self.assertEqual(result, [])

    @mock.patch('vcs_extension.vcs_extension.VcsExtension._get_critical_cs')
    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_critical_service_standby_node')
    @mock.patch('vcs_extension.vcs_extension.condense_name')
    def test_get_critical_service_ordering_neg(self, m_condense, mock_standby, mock_get_cs):
        mock_get_cs.return_value = self.priority_service
        m_condense.return_value = "Grp_CS_c1_sg_neo4j_clustered_service"
        mock_standby.return_value = []

        result = self.ext.get_critical_service_ordering(self.plugin_api_context, self.cluster)

        self.assertEqual(result, [])

    def test_get_critical_service_standby_node_pos(self):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'ONLINE'
        result = self.ext.get_critical_service_standby_node(self.plugin_api_context, self.cluster,
                                                            self.priority_service,
                                                            "Grp_CS_c1_sg_neo4j_clustered_service")
        self.assertEqual(result, ['n1', 'n2', 'n3', 'n4'])

    def test_get_critical_service_standby_node_neg(self):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.result['node1']['data']['out'] = None
        self.result['node2']['data']['out'] = None

        self.assertRaises(ViewError, self.ext.get_critical_service_standby_node, self.plugin_api_context,
                          self.cluster, self.priority_service, "Grp_CS_c1_sg_neo4j_clustered_service")

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_critical_service_standby_node_both_starting(self, log):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.priority_service.item_id = "Grp_CS_c1_sg_neo4j_clustered_service"
        self.result['node1']['data']['out'] = 'STARTING'
        self.result['node2']['data']['out'] = 'STARTING'

        self.assertRaises(ViewError, self.ext.get_critical_service_standby_node, self.plugin_api_context, self.cluster,
                          self.priority_service, "Grp_CS_c1_sg_neo4j_clustered_service")

        self.assert_(mock.call('The status of the critical service \"Grp_CS_c1_sg_neo4j_clustered_service\" '
                               'on the node \"node2\" cannot be determined.') in
                     log.trace.error.call_args_list)
        self.assert_(mock.call('Output of group state: STARTING') in log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_critical_service_standby_node_both_online(self, log):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.priority_service.item_id = "Grp_CS_c1_sg_neo4j_clustered_service"
        self.result['node1']['data']['out'] = 'ONLINE'
        self.result['node2']['data']['out'] = 'ONLINE'

        self.assertRaises(ViewError, self.ext.get_critical_service_standby_node, self.plugin_api_context, self.cluster,
                          self.priority_service, "Grp_CS_c1_sg_neo4j_clustered_service")

        self.assert_(mock.call('The status of the critical '
                               'service \"Grp_CS_c1_sg_neo4j_clustered_service\" '
                               'is online on both nodes on '
                               'the cluster \"{0}\".'.format(self.cluster.item_id)) in
                     log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_critical_service_standby_node_both_offline(self, log):
        self.cluster.nodes = [self.n1, self.n2, self.n3, self.n4]
        self.priority_service.item_id = "Grp_CS_foo_sg_neo4j_clustered_service"
        self.result['node1']['data']['out'] = 'OFFLINE'
        self.result['node2']['data']['out'] = 'OFFLINE'

        nodes = self.ext.get_critical_service_standby_node(
            self.plugin_api_context, self.cluster,
            self.priority_service, "Grp_CS_foo_sg_neo4j_clustered_service")

        self.assertEquals(['n2', 'n1', 'n3', 'n4'], nodes)
        self.assert_(mock.call('The status of the critical '
                               'service \"Grp_CS_foo_sg_neo4j_clustered_service\" '
                               'is offline on both nodes on '
                               'the cluster \"{0}\".'.format(self.cluster.item_id)) in
                     log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_critical_service_ordering')
    @mock.patch('vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    def test_get_node_upgrade_ordering_cs_pos(self, m_ffl, mock_get_cs):
        m_ffl.return_value = []
        mock_get_cs.return_value = ['n1', 'n2', 'n3', 'n4']

        result = self.ext.get_node_upgrade_ordering(self.plugin_api_context, self.cluster)
        self.assertEqual(result, ['n1', 'n2', 'n3', 'n4'])

    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_critical_service_ordering')
    @mock.patch('vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_node_upgrade_ordering_cs_neg(self, log, m_ffl, mock_get_cs):
        m_ffl.return_value = ["n2", "n1", "n3"]
        mock_get_cs.return_value = []

        result = self.ext.get_node_upgrade_ordering(self.plugin_api_context, self.cluster)
        self.assert_(mock.call('node_upgrade_ordering handled by core') in
                     log.trace.debug.call_args_list)
        self.assertEqual(result, [])

    def setUp_ffl_sg(self, is_node_inital=False, os_reinstall=''):
        self.ext = VcsExtension()

        self.plugin_api_context = mock.Mock()

        self.upgrade = mock.Mock(os_reinstall=os_reinstall)
        self.n1 = mock.Mock(item_id='n1', hostname='node1', is_for_removal=lambda: False, is_initial=lambda: is_node_inital, query=mock.Mock(return_value=[self.upgrade]))
        self.n2 = mock.Mock(item_id='n2', hostname='node2', is_for_removal=lambda: False, is_initial=lambda: is_node_inital)
        self.n3 = mock.Mock(item_id='n3', hostname='node3', is_for_removal=lambda: False, is_initial=lambda: is_node_inital, query=mock.Mock(return_value=[self.upgrade]))
        self.n4 = mock.Mock(item_id='n4', hostname='node4', is_for_removal=lambda: False, is_initial=lambda: is_node_inital, query=mock.Mock(return_value=[self.upgrade]))

        self.cluster = mock.Mock(nodes=[self.n1 , self.n2, self.n3, self.n4],
                                 is_initial=lambda: is_node_inital,
                                 is_for_removal=lambda: False,
                                 llt_nets="",
                                 item_id='foo',
                                 vpath='/foo/foo')
        self.neo4j_service = [mock.Mock(item_id='sg_neo4j_clustered_service',
                                        node_list='n2,n1,n3',
                                        name="neo4j_cluster_service")]
        self.cluster.services = self.neo4j_service

        def side_effect(*args, **kwargs):
            if args[0] == 'vcs-clustered-service':
                return self.neo4j_service
            elif args[0] == 'node' and kwargs['hostname'] == 'node1':
                return [self.n1]
            elif args[0] == 'node' and kwargs['hostname'] == 'node2':
                return [self.n2]
            elif args[0] == 'node' and kwargs['hostname'] == 'node3':
                return [self.n3]
            elif args[0] == 'node' and kwargs['hostname'] == 'node4':
                return [self.n4]

        self.cluster.query.side_effect = side_effect

    def test_get_leader_node_from_cluster_model(self):
        self.assertEqual(self.ext.get_leader_node_from_cluster_model(
            self.cluster, "node1"), 'n1')

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_cluster_model_neg(self, log):
        self.setUp_ffl_sg()

        self.ext.get_leader_node_from_cluster_model(
            self.cluster, "bad_node1")

        self.assert_(mock.call('Node hostname \"bad_node1\" in FFL overview not found in cluster \"/foo/foo\"')
                     in log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_cluster_model')
    def test_get_leader_node_from_ffl_overview_dps_leader(self, m_get_node):
        self.setUp_ffl_sg()
        m_get_node.return_value = 'n1'

        self.assertEqual(self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_JSON, 'dps'), 'n1')

    def test_get_leader_node_from_ffl_overview_system_leader(self):
        self.setUp_ffl_sg()

        self.assertEqual(self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_JSON, 'system'), 'n3')

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_incorrect_key(self, log):
        self.setUp_ffl_sg()

        self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_JSON, 'blah')
        self.assert_(mock.call('Element passed is not correct. '
                               'It must be \'dps\' or \'system\' to find the DPS or System Leaders.')
                     in log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_bad_system_leader_hostname(self, log):
        self.setUp_ffl_sg()
        self.cluster.query.side_effect = [[], [], []]

        self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_BAD_HOSTNAME, 'system')

        self.assert_(mock.call('Node hostname "bad_nde3" in FFL overview not '
                               'found in cluster "{0}"'.format(self.cluster.vpath))
                     in log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_bad_dps_leader_hostname(self, log):
        self.setUp_ffl_sg()
        self.cluster.query.side_effect = [[], [], []]

        self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_BAD_HOSTNAME, 'dps')

        self.assert_(mock.call('Node hostname "bad_nde1" in FFL overview not '
                               'found in cluster "{0}"'.format(self.cluster.vpath))
                     in log.trace.error.call_args_list)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_no_hostname_key_in_overview(self, log):
        self.setUp_ffl_sg()

        nodes = self.ext.get_leader_node_from_ffl_overview(self.cluster, FFL_OVERVIEW_NO_HOSTNAME, 'system')
        self.assert_(mock.call("Unable to parse FFL overview as key 'hostname' not found") in
                     log.trace.error.call_args_list)
        self.assertEqual(nodes, None)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_no_dps_leader_in_overview(self, log):
        self.setUp_ffl_sg()

        self.assertEqual(self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_NO_DPS, 'dps'), None)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_no_dps_leader_key_in_overview(self, log):
        self.setUp_ffl_sg()

        nodes = self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_NO_DPS_KEY, 'dps')
        self.assertEqual(nodes, None)
        self.assert_(
            mock.call("Unable to parse FFL overview as key 'dps' not found") in log.trace.error.call_args_list)

    def test_get_leader_node_from_ffl_overview_no_system_leader_in_overview(self):
        self.setUp_ffl_sg()
        self.assertEqual(self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_NO_SYSTEM, 'system'), None)

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_leader_node_from_ffl_overview_no_system_leader_key_in_overview(self, log):
        self.setUp_ffl_sg()
        nodes = self.ext.get_leader_node_from_ffl_overview(
            self.cluster, FFL_OVERVIEW_NO_SYSTEM_KEY, 'system')
        self.assertEqual(nodes, None)
        self.assert_(
            mock.call("Unable to parse FFL overview as key 'system' not found") in log.trace.error.call_args_list)

    def test_get_leader_node_from_ffl_overview_bad_json(self):
        self.result = {
            'node1': {'data': {'out': False}},
            'node2': {'data': {'out': False}}
        }

        jstr = [{"addresses": {"http": "1ef8343"}}]
        self.setUp_ffl_sg()

        self.ext.get_leader_node_from_ffl_overview(
            self.cluster, jstr, 'dps')

        self.assert_(mock.call("Unable to parse FFL overview as key 'host' not found"))

    def test_get_leader_node_from_ffl_overview_no_neo4j_data(self):
        self.result = {
            'node1': {'data': {'out': False}},
            'node2': {'data': {'out': False}}
        }
        self.setUp_ffl_sg()
        jstr = []

        self.assertEqual(self.ext.get_leader_node_from_ffl_overview(
            self.cluster, jstr, 'dps'), None)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_ffl_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def get_causal_cluster_ffl_ordering_no_ffl_overview(self, log, mock_get_leader, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = None
        mock_get_leader.side_effect = iter([None, None])
        mock_node_list.return_value = ["n3", "n1", "n2"]

        self.ext.get_causal_cluster_ffl_ordering(self.plugin_api_context, self.cluster, mock_node_list.return_value)
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_ffl_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_causal_cluster_ffl_ordering_no_dps_leader(self, log, mock_get_leader, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = [{"addresses": {"http": "1ef8343"}}]
        mock_get_leader.side_effect = iter(['n3', None])
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.ext.get_causal_cluster_ffl_ordering(self.plugin_api_context, self.cluster, mock_node_list.return_value)
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_ffl_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_causal_cluster_ffl_ordering_no_system_leader(self, log, mock_get_leader, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = [{"addresses": {"http": "1ef8343"}}]
        mock_get_leader.side_effect = iter([None, 'n1'])
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.ext.get_causal_cluster_ffl_ordering(self.plugin_api_context, self.cluster, mock_node_list.return_value)
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_ffl_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_causal_cluster_ffl_ordering_no_leaders(self, log, mock_get_leader, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = [{"addresses": {"http": "1ef8343"}}]
        mock_get_leader.side_effect = iter([None, None])
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.ext.get_causal_cluster_ffl_ordering(self.plugin_api_context, self.cluster, mock_node_list.return_value)
        self.ext.get_leader_node_from_ffl_overview.assert_called_once()
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_leader_node_from_ffl_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_causal_cluster_ffl_ordering_return_leaders(self, log, mock_get_leader, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = [{"addresses": {"http": "1ef8343"}}]
        mock_get_leader.side_effect = iter(['n1', 'n3'])
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.assertEqual(self.ext.get_causal_cluster_ffl_ordering(
            self.plugin_api_context, self.cluster, mock_node_list.return_value),
            ['n4', 'n2', 'n1', 'n3'])

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    def test_get_causal_cluster_ffl_ordering_pos(self, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = FFL_OVERVIEW_JSON
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.assertEqual(self.ext.get_causal_cluster_ffl_ordering(
            self.plugin_api_context, self.cluster, mock_node_list.return_value),
            ['n4', 'n2', 'n3', 'n1'])

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    def test_get_causal_cluster_ffl_ordering_pos_diff_list_order(self, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = FFL_OVERVIEW_JSON
        mock_node_list.return_value = ["n3", "n2", "n1"]

        self.assertEqual(self.ext.get_causal_cluster_ffl_ordering(
            self.plugin_api_context, self.cluster, mock_node_list.return_value),
            ['n4', 'n2', 'n3', 'n1'])

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    def test_get_causal_cluster_ffl_ordering_pos_another_diff_list_order(self, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = FFL_OVERVIEW_JSON
        mock_node_list.return_value = ["n2", "n1", "n3"]

        self.assertEqual(self.ext.get_causal_cluster_ffl_ordering(
            self.plugin_api_context, self.cluster, mock_node_list.return_value),
            ['n4', 'n2', 'n3', 'n1'])

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_get_causal_cluster_ffl_ordering_neg(self, log, mock_overview, mock_node_list):
        self.setUp_ffl_sg()
        mock_overview.return_value = FFL_OVERVIEW_NO_SYSTEM
        mock_node_list.return_value = ["n1", "n2", "n3"]

        self.ext.get_causal_cluster_ffl_ordering(self.plugin_api_context, self.cluster, mock_node_list.return_value)
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    def test_node_ordering_ffl_pos(self, mock_overview, mock_is_ffl):
        self.result = {
            'node1': {'data': {'out': False}},
            'node2': {'data': {'out': False}}
        }

        self.setUp_ffl_sg()
        mock_is_ffl.return_value = ["n2", "n1", "n3"]
        self.plugin_api_context.rpc_command.return_value = self.result
        mock_overview.return_value = FFL_OVERVIEW_JSON

        self.assertEqual(self.ext.get_node_upgrade_ordering(
            self.plugin_api_context, self.cluster),
            ['n4', 'n2', 'n3', 'n1'])

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_node_ordering_ffl_not_in_use(self, log, mock_ffl_in_use):
        self.setUp_ffl_sg()
        mock_ffl_in_use.return_value = []

        self.ext.get_node_upgrade_ordering(
            self.plugin_api_context, self.cluster)

        self.assert_(mock.call('node_upgrade_ordering handled by core') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_node_ordering_ffl_bad_json(self, log, mock_overview):
        self.result = {
            'node1': {'data': {'out': False}},
            'node2': {'data': {'out': False}}
        }
        jstr = [{"addresses": {"http": "1ef8343"}}]
        self.setUp_ffl_sg()

        self.plugin_api_context.rpc_command.return_value = self.result
        mock_overview.return_value = jstr

        self.ext.get_node_upgrade_ordering(
            self.plugin_api_context, self.cluster)

        self.assert_(mock.call("Unable to parse FFL overview as key 'host' not found"))
        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                     log.trace.debug.call_args_list)
        self.assert_(mock.call('node_upgrade_ordering handled by core') in
                     log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.is_ffl_in_use')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_node_ordering_ffl_bad_hostname_in_overview(self, log, mock_is_ffl, mock_overview):
        self.setUp_ffl_sg()
        mock_is_ffl.return_value = ["n2", "n1", "n3"]
        mock_overview.return_value = FFL_OVERVIEW_BAD_HOSTNAME
        self.cluster.query.side_effect = [[], [], []]

        self.ext.get_node_upgrade_ordering(
            self.plugin_api_context, self.cluster)

        self.assert_(mock.call('Node hostname "bad_nde3" in FFL overview not '
                               'found in cluster "{0}"'.format(self.cluster.vpath))
                     in log.trace.error.call_args_list)
        self.assert_(mock.call('node_upgrade_ordering handled by core')
                     in log.trace.debug.call_args_list)

    @mock.patch(
        'vcs_extension.vcs_extension.VcsExtension.get_ffl_cluster_overview')
    @mock.patch('vcs_extension.vcs_extension.log')
    def test_node_ordering_ffl_no_neo4j_data(self, log, mock_overview):
        self.result = {
            'node1': {'data': {'out': False}},
            'node2': {'data': {'out': False}}
        }
        self.setUp_ffl_sg()
        self.plugin_api_context.rpc_command.return_value = self.result
        mock_overview.return_value = []
        self.ext.get_node_upgrade_ordering(
            self.plugin_api_context, self.cluster)

        self.assert_(mock.call('Ordered node list could not be created using FFL data') in
                      log.trace.debug.call_args_list)
        self.assert_(mock.call('node_upgrade_ordering handled by core') in
                      log.trace.debug.call_args_list)

    def test_get_ffl_cluster_overview_pos(self):
        self.setUp_ffl_sg()
        jstr_raw = {'node2': {'errors': u'', 'data': {u'retcode': 0, u'err': u'',
                                                  u'out': u'{"instances": [{"addresses": {"http": "10.247.246.10:7474", "bolt": "10.247.246.10:7687", "https": "10.247.246.10:7473"}, "database": "default", "cypher_available": true, "host": {"ip": "10.247.246.10", "hostname": "node2", "aliases": ["n2"]}, "version": "3.5.3", "role": "LEADER", "groups": [], "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {"addresses": {"http": "10.247.246.16:7474", "bolt": "10.247.246.16:7687", "https": "10.247.246.16:7473"}, "database": "default", "cypher_available": false, "host": {"ip": "10.247.246.16", "hostname": "node3", "aliases": ["n3"]}, "version": "3.5.3", "role": "FOLLOWER", "groups": [], "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {"addresses": {"http": "10.247.246.17:7474", "bolt": "10.247.246.17:7687", "https": "10.247.246.17:7473"}, "database": "default", "cypher_available": true, "host": {"ip": "10.247.246.17", "hostname": "node4", "aliases": ["n4"]}, "version": "3.5.3", "role": "FOLLOWER", "groups": [], "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}], "cluster": {"mode": "cluster"}}'}}}
        jstr_instances = [{u'addresses': {u'http': u'10.247.246.10:7474', u'bolt': u'10.247.246.10:7687', u'https': u'10.247.246.10:7473'}, u'database': u'default', u'cypher_available': True, u'host': {u'ip': u'10.247.246.10', u'hostname': u'node2', u'aliases': [u'n2']}, u'version': u'3.5.3', u'role': u'LEADER', u'groups': [], u'id': u'04fe2502-a7eb-4145-bf62-dd336b08fcd1'}, {u'addresses': {u'http': u'10.247.246.16:7474', u'bolt': u'10.247.246.16:7687', u'https': u'10.247.246.16:7473'}, u'database': u'default', u'cypher_available': False, u'host': {u'ip': u'10.247.246.16', u'hostname': u'node3', u'aliases': [u'n3']}, u'version': u'3.5.3', u'role': u'FOLLOWER', u'groups': [], u'id': u'cfec7278-6097-4a4b-9a9e-df90eb70abff'}, {u'addresses': {u'http': u'10.247.246.17:7474', u'bolt': u'10.247.246.17:7687', u'https': u'10.247.246.17:7473'}, u'database': u'default', u'cypher_available': True, u'host': {u'ip': u'10.247.246.17', u'hostname': u'node4', u'aliases': [u'n4']}, u'version': u'3.5.3', u'role': u'FOLLOWER', u'groups': [], u'id': u'e8842851-465f-43c2-9dd7-d4f456ef8343'}]
        self.plugin_api_context.rpc_command.return_value = jstr_raw
        self.assertEqual(self.ext.get_ffl_cluster_overview(self.plugin_api_context,
                                            self.cluster), jstr_instances)

    def test_get_ffl_cluster_overview_no_data(self):
        self.setUp_ffl_sg()
        jstr_raw = {'node2': {'errors': u'', 'data':  {"retcode": 'foo', "out": None, "err": 'foo'}}}
        self.plugin_api_context.rpc_command.return_value = jstr_raw
        self.assertEqual(self.ext.get_ffl_cluster_overview(self.plugin_api_context,
                                            self.cluster), [])

    def test_get_ffl_cluster_overview_no_instance(self):
        self.setUp_ffl_sg()
        jstr_raw = {'node2': {'errors': u'', 'data': {u'retcode': 0, u'err': u'',
                                                  u'out': u'{"foo": [{"addresses": {"http": "10.247.246.10:7474", "bolt": "10.247.246.10:7687", "https": "10.247.246.10:7473"}, "database": "default", "cypher_available": true, "host": {"ip": "10.247.246.10", "hostname": "node2", "aliases": ["n2"]}, "version": "3.5.3", "role": "LEADER", "groups": [], "id": "04fe2502-a7eb-4145-bf62-dd336b08fcd1"}, {"addresses": {"http": "10.247.246.16:7474", "bolt": "10.247.246.16:7687", "https": "10.247.246.16:7473"}, "database": "default", "cypher_available": false, "host": {"ip": "10.247.246.16", "hostname": "node3", "aliases": ["n3"]}, "version": "3.5.3", "role": "FOLLOWER", "groups": [], "id": "cfec7278-6097-4a4b-9a9e-df90eb70abff"}, {"addresses": {"http": "10.247.246.17:7474", "bolt": "10.247.246.17:7687", "https": "10.247.246.17:7473"}, "database": "default", "cypher_available": true, "host": {"ip": "10.247.246.17", "hostname": "node4", "aliases": ["n4"]}, "version": "3.5.3", "role": "FOLLOWER", "groups": [], "id": "e8842851-465f-43c2-9dd7-d4f456ef8343"}], "cluster": {"mode": "cluster"}}'}}}
        self.plugin_api_context.rpc_command.return_value = jstr_raw
        self.assertEqual(self.ext.get_ffl_cluster_overview(self.plugin_api_context,
                                            self.cluster), [])

    def test_is_ffl_in_use_true(self):
        self.result = {
            'node1' : { 'data' : {'out' : False }},
        }
        self.setUp_ffl_sg()
        self.plugin_api_context.rpc_command.return_value = self.result
        self.assertTrue(self.ext.is_ffl_in_use(
            self.plugin_api_context, self.cluster))

    @mock.patch('vcs_extension.vcs_extension.log')
    def test_is_ffl_in_use_rpc_return_nothing(self, log):

        self.setUp_ffl_sg()
        self.plugin_api_context.rpc_command.return_value = {}
        self.assertFalse(self.ext.is_ffl_in_use(
            self.plugin_api_context, self.cluster))
        self.assert_(mock.call('Unable to check if service group "Grp_CS_foo_sg_neo4j_clustered_service" on node "node3" is frozen: ')
                     in log.trace.error.call_args_list)

    def test_is_ffl_in_use_false(self):
        self.result = {
            'node1' : { 'data' : {'out' : True }},
            'node2' : { 'data' : {'out' : True }},
            'node3' : { 'data' : {'out' : True }},
            'node4' : { 'data' : {'out' : True }},
        }
        self.setUp_ffl_sg()
        self.plugin_api_context.rpc_command.return_value = self.result
        self.assertFalse(self.ext.is_ffl_in_use(
            self.plugin_api_context, self.cluster))

    def test_is_os_reinstall_on_peer_nodes(self):
        self.plugin_api_context = mock.Mock()
        cluster = mock.Mock(critical_service='MockService')
        node1 = mock.Mock(item_id='n1', hostname='node1', item_type_id="node")
        node2 = mock.Mock(item_id='n2', hostname='node2', item_type_id="node")
        upgrade_false = mock.Mock(item_id='upgrade', os_reinstall='false')
        upgrade_true = mock.Mock(item_id='upgrade', os_reinstall='true')
        cluster.nodes = [node1, node2]

        cluster.get_cluster.return_value = cluster
        cluster.nodes = [node1, node2]
        node1.query.side_effect = [[upgrade_true], [upgrade_false],
                                   [upgrade_true], [], [upgrade_false], []]
        node2.query.side_effect = [[upgrade_true], [upgrade_true],
                                   [upgrade_false], [upgrade_true],
                                   [upgrade_false], []]

        # Assert True if os_reinstall=="true" on any node
        self.assertTrue(self.ext.is_os_reinstall_on_peer_nodes(cluster))
        self.assertTrue(self.ext.is_os_reinstall_on_peer_nodes(cluster))
        self.assertTrue(self.ext.is_os_reinstall_on_peer_nodes(cluster))
        self.assertTrue(self.ext.is_os_reinstall_on_peer_nodes(cluster))
        # Assert False if os_reinstall!="true" on any node
        self.assertFalse(self.ext.is_os_reinstall_on_peer_nodes(cluster))
        # Assert True if no upgrade item
        self.assertFalse(self.ext.is_os_reinstall_on_peer_nodes(cluster))

    def test_get_package_file_info(self):
        all_pkgs = """/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1062.el7.x86_64.debug
/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1127.el7.x86_64.debug
/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-123.el7.x86_64.debug
/etc/vx/kernel/vxspec.ko.3.10.0-957.el7.x86_64"""

        self.result = {
            'node1': {'data': {'out': all_pkgs}}
        }
        self.plugin_api_context.rpc_command.return_value = self.result
        all_pkgs_list = ['/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-123.el7.x86_64.debug',
                         '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1062.el7.x86_64.debug',
                         '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1127.el7.x86_64.debug']
        greps = ["/opt", ".debug"]
        self.assertEqual(all_pkgs_list, self.ext.get_package_file_info(
            self.plugin_api_context, self.n1.hostname, "VRTSvxvm.x86_64", greps))

    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_current_kernel_version')
    def test_get_latest_debug_file(self, mock_kernel_ver):
        mock_kernel_ver.return_value = "3.10.0-1160"
        debug_files = ['/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-123.el7.x86_64.debug',
                       '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1062.el7.x86_64.debug',
                       '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1127.el7.x86_64.debug'
                       ]

        self.assertEqual("3.10.0-1127", self.ext.get_latest_debug_file(
            self.n1.hostname, debug_files))

    @mock.patch('vcs_extension.vcs_extension.log')
    @mock.patch('vcs_extension.vcs_extension.VcsExtension.get_current_kernel_version')
    def test_remove_unused_vrts_debug_files(self, mock_kernel_ver, mock_log):
        mock_kernel_ver.return_value = "3.10.0-1160"
        debug_files = [
            '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-123.el7.x86_64.debug',
            '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1062.el7.x86_64.debug',
            '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1127.el7.x86_64.debug'
            ]
        self.plugin_api_context.rpc_command.side_effect = [
            {'node1': {'data': {'out': True}}},
            "Deleted {0}".format(debug_files[0]),
            {'node1': {'data': {'out': True}}},
            "Deleted {0}".format(debug_files[1]),
            {'node1': {'data': {'out': True}}},
            "Deleted {0}".format(debug_files[2])
        ]
        self.ext.remove_unused_vrts_debug_files(self.plugin_api_context, self.n1.hostname, debug_files)
        mock_log.trace.info.assert_has_calls([
            mock.call("Node node1: Remove all debuginfo files except for version '3.10.0-1127'"),
            mock.call("Node node1: Delete File '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-123.el7.x86_64.debug'"),
            mock.call("Node node1: Delete File '/opt/VRTSvxvm/debuginfo/7.3.1.3302/vxdmp.ko.3.10.0-1062.el7.x86_64.debug'")]
        )

class TestCondenseName(unittest.TestCase):

    def test_string_length_78(self):
        name = "Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_156_10_10_10_157_10_10_10_158"
        expected_condensed_string = 'Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_1_4bf2fb7b'

        self.assertEqual(condense_name(name), expected_condensed_string)

    def test_string_length_59(self):
        name = "Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_156_10_10_"
        expected_condensed_string = 'Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_156_10_10_'

        self.assertEqual(condense_name(name), expected_condensed_string)

    def test_string_length_60(self):
        name = "Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_156_10_10_1"
        expected_condensed_string = 'Res_IP_cluster1_cs1_apache_10_10_10_155_10_10_10_1_94f0c9d9'

        self.assertEqual(condense_name(name), expected_condensed_string)


if __name__ == '__main__':
    unittest.main()
