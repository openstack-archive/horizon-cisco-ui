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

import json
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

        message = json.dumps(network)
        with mock.patch.object(self.client.clnt, 'call') as mock_call:
            self.client.associate_profile_with_network(network)

        mock_call.assert_called_with({}, 'associate_profile_with_network',
                                     msg=message)

    def test_associate_profile_with_network_rpc_exception(self):
        network = dict(id='1125-as45-afg5f-3457',
                       cfgp='defaultNetworkL2Profile',
                       name='net1',
                       tenant_id=1)

        with mock.patch.object(self.client.clnt, 'call',
                               side_effect=dfa_client.messaging.MessagingException), \
                self.assertRaises(dfa_client.exceptions.NotAvailable) as cm:
            self.client.associate_profile_with_network(network)

        self.assertEqual('RPC to Fabric Enabler failed',
                         str(cm.exception))
