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
            {},
            'associate_profile_with_network',
            msg=network)

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

'''
    def test_do_associate_dci_id_to_project(self):
        tenant = dict(tenant_id=1,
                      tenant_name='Project1',
                      dci_id=1001)

        message = json.dumps(tenant)
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'cast') as mock_cast:
            self.DFAClient.do_associate_dci_id_to_project(tenant)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('associate_dci_id_to_project', {},
                                         msg=message)
        mock_cast.assert_called_with(rpc_make_obj)

    def test_get_fabric_summary(self):
        summary = dict(fabric_enabler_version='2.0',
                       dcnm_version='10.0(1)',
                       dcnm_ip='10.10.1.24',
                       fabric_id=2,
                       fabric_type='vxlan')

        message = json.dumps({})
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=summary) as mock_call:
            resp = self.DFAClient.get_fabric_summary()

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_fabric_summary', {}, msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(summary, resp)

    def test_get_config_profiles_detail(self):
        config_p = dict(tenant_id=1,
                        tenant_name='Project1',
                        dci_id=1001)

        message = json.dumps({})
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=config_p) as mock_call:
            resp = self.DFAClient.get_config_profiles_detail()

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_config_profiles_detail', {},
                                         msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(config_p, resp)

    def test_get_project_details(self):
        project_details = dict(project_id=1,
                               project_name='Project1',
                               seg_id=12001,
                               dci_id=1001,
                               result='SUCCESS')

        tenant = dict(tenant_id=1)
        message = json.dumps(tenant)
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=project_details) as mock_call:
            resp = self.DFAClient.get_project_details(tenant)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_project_detail', {}, msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(project_details, resp)

    def test_get_network_by_tenant_id(self):
        network_details = dict(network_name='NET1',
                               network_id='1001-1001',
                               config_profile='defaultNetworkEVPNProfile',
                               seg_id=12001,
                               vlan_id=1001,
                               result='SUCCESS')

        tenant = dict(tenant_id=1)
        message = json.dumps(tenant)
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=network_details) as mock_call:
            resp = self.DFAClient.get_network_by_tenant_id(tenant)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_all_networks_for_tenant', {},
                                         msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(network_details, resp)

    def test_get_instance_by_tenant_id(self):
        instance_details = dict(network_name='NET1',
                                network_id='1001-1001',
                                config_profile='defaultNetworkEVPNProfile',
                                seg_id=12001,
                                vlan_id=1001,
                                result='SUCCESS')

        tenant = dict(tenant_id=1)
        message = json.dumps(tenant)
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=instance_details) as mock_call:
            resp = self.DFAClient.get_instance_by_tenant_id(tenant)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_instance_by_tenant_id', {},
                                         msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(instance_details, resp)

    def test_get_agents_details(self):
        agent_details = dict(network_name='NET1',
                             network_id='1001-1001',
                             config_profile='defaultNetworkEVPNProfile',
                             seg_id=12001,
                             vlan_id=1001,
                             result='SUCCESS')

        message = json.dumps({})
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=agent_details) as mock_call:
            resp = self.DFAClient.get_agents_details()

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_agents_details', {}, msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(agent_details, resp)

    def test_get_agent_details_per_host(self):
        agent_details = dict(network_name='NET1',
                             network_id='1001-1001',
                             config_profile='defaultNetworkEVPNProfile',
                             seg_id=12001,
                             vlan_id=1001,
                             result='SUCCESS')

        agent = dict(tenant_id=1)
        message = json.dumps(agent)
        with mock.patch.object(self.DFAClient.clnt,
                               'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call',
                                  return_value=agent_details) as mock_call:
            resp = self.DFAClient.get_agent_details_per_host(agent)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('get_agent_details_per_host', {},
                                         msg=message)
        mock_call.assert_called_with(rpc_make_obj)
        self.assertEqual(agent_details, resp)
'''
