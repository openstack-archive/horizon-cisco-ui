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

import logging
import json
import platform
import sys

from networking_cisco.apps.saf.server import cisco_dfa_rest as cdr
from networking_cisco.apps.saf.common import config
from networking_cisco.apps.saf.common import constants
from networking_cisco.apps.saf.common import rpc

from horizon import exceptions as hexc

LOG = logging.getLogger(__name__)


class DFAClient():
    """Client to interact with Fabric Enabler via RPC"""

    def __init__(self):
        self.ctl_host = platform.node()
        self._cfg = config.CiscoDFAConfig().cfg
        self.setup_client_rpc()

    def setup_client_rpc(self):
        url = self._cfg.dfa_rpc.transport_url % (
            {'ip': self.ctl_host})
        self.clnt = rpc.DfaRpcClient(url, constants.DFA_SERVER_QUEUE,
                                     exchange=constants.DFA_EXCHANGE)

    def do_precreate_network(self, network):
        '''Precreate network on current version of Fabric Enabler'''

        context = {}
        args = json.dumps(network)
        msg = self.clnt.make_msg('precreate_network', context, msg=args)
        try:
            resp = self.clnt.call(msg)
            if not resp:
                raise hexc.NotAvailable("Project %(id)s not present in "
                                        "fabric enabler" %
                                        {'id': network.get('tenant_id')})
            return resp
        except (rpc.MessagingTimeout, rpc.RPCException, rpc.RemoteError):
            LOG.error("RPC: Request to precreate network failed.")
            raise hexc.NotAvailable("RPC to Fabric Enabler failed")

    def do_delete_precreate_network(self, network):
        '''Delete precreated network on current version of Fabric Enabler'''

        context = {}
        args = json.dumps(network)
        msg = self.clnt.make_msg('delete_precreate_network', context, msg=args)
        try:
            resp = self.clnt.call(msg)
            if not resp:
                raise hexc.NotAvailable("Project %(id)s not present in "
                                        "fabric enabler" %
                                        {'id': network.get('tenant_id')})
            return resp
        except (rpc.MessagingTimeout, rpc.RPCException, rpc.RemoteError):
            LOG.error("RPC: Request to delete precreated network failed.")
            raise hexc.NotAvailable("RPC to Fabric Enabler failed")

    def get_all_config_profiles(self):
        '''Get all Config Profiles from current version of Fabric Enabler'''

        context = {}
        args = json.dumps({})
        msg = self.clnt.make_msg('get_config_profiles', context, msg=args)
        try:
            resp = self.clnt.call(msg)
            return resp
        except (rpc.MessagingTimeout, rpc.RPCException, rpc.RemoteError):
            LOG.error("RPC: Request for Config Profiles failed.")
            raise hexc.NotAvailable("RPC to Fabric Enabler failed")


def dfa_client():
    if len(sys.argv[1:]) % 2:
        sys.argv.append("")
    sys.argv.append('--config-file')
    sys.argv.append('/etc/saf/enabler_conf.ini')
    return DFAClient()
