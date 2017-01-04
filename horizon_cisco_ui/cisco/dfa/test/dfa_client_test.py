# Copyright 2014 Cisco Systems, Inc.
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
import platform

from horizon_cisco_ui.cisco.dfa import dfa_client
from openstack_dashboard.test import helpers as test


class DFAClientTestCase(test.BaseAdminViewTests):

    def setUp(self):
        '''Setup routine '''
        super(DFAClientTestCase, self).setUp()
        self.ip = platform.node()
        self._test_dfa_client_init()

    def _test_dfa_client_init(self):
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.ConfigParser.ConfigParser'), \
                mock.patch('oslo_messaging.RPCClient'), \
                mock.patch('oslo_messaging.get_transport'):
            self.client = dfa_client.DFAClient()

    def test_do_associate_profile_with_network(self):
        network = dict(id='1125-as45-afg5f-3457',
                       cfgp='defaultNetworkL2Profile',
                       name='net1',
                       tenant_id=1)

        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            dfa_client.associate_profile_with_network(network)

        mock_client.return_value.call.assert_called_with(
            {}, 'associate_profile_with_network', msg=network)

    def test_associate_profile_with_network_rpc_exception(self):
        network = dict(id='1125-as45-afg5f-3457',
                       cfgp='defaultNetworkL2Profile',
                       name='net1',
                       tenant_id=1)

        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as mock_client, \
                self.assertRaises(dfa_client.exceptions.NotAvailable) as cm:
            mock_client.return_value.call = mock.MagicMock(
                side_effect=dfa_client.messaging.MessagingException)
            dfa_client.associate_profile_with_network(network)

        self.assertEqual('RPC to Fabric Enabler failed',
                         str(cm.exception))

    def test_do_associate_dci_id_to_project(self):
        tenant = dict(tenant_id=1,
                      tenant_name='Project1',
                      dci_id=1001)

        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.cast = mock.MagicMock()
            dfa_client.do_associate_dci_id_to_project(tenant)

        mock_client.return_value.cast.assert_called_with(
            {}, 'associate_dci_id_to_project', msg=tenant)

    def test_get_fabric_summary(self):
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_fabric_summary()
        mock_client.return_value.call.assert_called_with(
            {}, 'get_fabric_summary', msg={})
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_config_profiles_detail(self):
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_config_profiles_detail()

        mock_client.return_value.call.assert_called_with(
            {}, 'get_config_profiles_detail', msg={})
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_project_details(self):
        tenant = dict(tenant_id=1)
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_project_details(tenant)

        mock_client.return_value.call.assert_called_with(
            {}, 'get_project_detail', msg=tenant)
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_network_by_tenant_id(self):
        tenant = dict(tenant_id=1)
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_network_by_tenant_id(tenant)

        mock_client.return_value.call.assert_called_with(
            {}, 'get_all_networks_for_tenant', msg=tenant)
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_instance_by_tenant_id(self):
        tenant = dict(tenant_id=1)
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_instance_by_tenant_id(tenant)

        mock_client.return_value.call.assert_called_with(
            {}, 'get_instance_by_tenant_id', msg=tenant)
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_agents_details(self):
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_agents_details()

        mock_client.return_value.call.assert_called_with(
            {}, 'get_agents_details', msg={})
        self.assertEqual(resp, mock_client.return_value.call.return_value)

    def test_get_agent_details_per_host(self):
        agent = dict(tenant_id=1)
        with mock.patch('horizon_cisco_ui.cisco.dfa.dfa_client.dfaclient') as \
                mock_client:
            mock_client.return_value.call = mock.MagicMock()
            resp = dfa_client.get_agent_details_per_host(agent)

        mock_client.return_value.call.assert_called_with(
            {}, 'get_agent_details_per_host', msg=agent)
        self.assertEqual(resp, mock_client.return_value.call.return_value)
