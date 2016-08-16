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
import unittest

from horizon_cisco_ui.cisco.dfa import dfa_client

from networking_cisco.apps.saf.common import config
from networking_cisco.apps.saf.common import constants


class DFAClientTestCase(unittest.TestCase):

    def setUp(self):
        '''Setup routine '''
        super(DFAClientTestCase, self).setUp()
        self.ip = platform.node()
        self._test_dfa_client_init()

    def _test_dfa_client_init(self):
        with mock.patch('networking_cisco.apps.saf.common.rpc.DfaRpcClient') as dfa_rpc, \
                mock.patch.object(config.CiscoDFAConfig, 'cfg') as dfa_cfg:
            self.DFAClient = dfa_client.DFAClient()
        self.url = dfa_cfg.dfa_rpc.transport_url % ({'ip': self.ip})
        dfa_rpc.assert_called_with(self.url,
                                   constants.DFA_SERVER_QUEUE,
                                   exchange=constants.DFA_EXCHANGE)

    def test_do_precreate_network(self):
        network = dict(tenant_id=1,
                       nwk_name='net1',
                       subnet='10.0.0.0/24',
                       cfgp='defaultNetworkL2Profile')

        message = json.dumps(network)
        with mock.patch.object(self.DFAClient.clnt, 'make_msg') as mock_make_msg, \
                mock.patch.object(self.DFAClient.clnt, 'call') as mock_call:
            self.DFAClient.do_precreate_network(network)

        rpc_make_obj = mock_make_msg.return_value
        mock_make_msg.assert_called_with('precreate_network', {}, msg=message)
        mock_call.assert_called_with(rpc_make_obj)

    def test_do_precreate_network_not_available_exception(self):
        network = dict(tenant_id=1,
                       nwk_name='net1',
                       subnet='10.0.0.0/24',
                       cfgp='defaultNetworkL2Profile')

        with mock.patch.object(self.DFAClient.clnt, 'call',
                               return_value=False), \
                self.assertRaises(dfa_client.hexc.NotAvailable) as cm:
            self.DFAClient.do_precreate_network(network)

        self.assertEqual('Project 1 not present in fabric enabler',
                         str(cm.exception))

    def test_do_precreate_network_rpc_exception(self):
        network = dict(tenant_id=1,
                       nwk_name='net1',
                       subnet='10.0.0.0/24',
                       cfgp='defaultNetworkL2Profile')

        with mock.patch.object(self.DFAClient.clnt, 'call',
                               side_effect=dfa_client.rpc.RPCException), \
                self.assertRaises(dfa_client.hexc.NotAvailable) as cm:
            self.DFAClient.do_precreate_network(network)

        self.assertEqual('RPC to Fabric Enabler failed',
                         str(cm.exception))


if __name__ == '__main__':
    unittest.main()
