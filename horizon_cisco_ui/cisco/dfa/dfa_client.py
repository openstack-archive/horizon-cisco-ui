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

import ConfigParser
import json
import logging
import platform

import oslo_messaging as messaging

from horizon import exceptions
from horizon.utils.memoized import memoized
from oslo_config import cfg

LOG = logging.getLogger(__name__)


class DFAClient(object):
    """Represents fabric enabler command line interface."""

    def __init__(self):
        self.setup_client()

    @memoized
    def setup_client(self):

        cfgfile = '/etc/saf/enabler_conf.ini'
        config = ConfigParser.ConfigParser()
        res = config.read(cfgfile)
        if not res:
            return None
        url = config.get('dfa_rpc', 'transport_url')
        self.ctl_host = platform.node()
        url = url % ({'ip': self.ctl_host})

        transport = messaging.get_transport(cfg.CONF, url=url)
        target = messaging.Target(exchange='dfa',
                                  topic='dfa_server_q', fanout=False)
        self.clnt = messaging.RPCClient(transport, target)

        return self.clnt

    def associate_profile_with_network(self, network):
            context = {}
            args = json.dumps(network)
            try:
                resp = self.clnt.call(context,
                                      'associate_profile_with_network',
                                      msg=args)
                return resp
            except (messaging.MessagingException, messaging.RemoteError,
                    messaging.MessagingTimeout):
                LOG.error("RPC: Request to associate profile with network"
                          " failed.")
                raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_config_profiles_detail(self):
        '''Get all config Profiles details from the Fabric Enabler'''

        context = {}
        args = json.dumps({})
        try:
            resp = self.clnt.call(context, 'get_config_profiles_detail',
                                  msg=args)
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for detailed Config Profiles failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")
