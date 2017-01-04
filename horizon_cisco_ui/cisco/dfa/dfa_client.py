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

from django.utils.translation import ugettext_lazy as _

try:
    import oslo_messaging as messaging
except ImportError:
    from oslo import messaging
try:
    from oslo_config import cfg
except ImportError:
    from oslo.config import cfg

from horizon import exceptions
from horizon.utils.memoized import memoized

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
            resp = self.clnt.call(context, 'associate_profile_with_network',
                                  msg=args)
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request to associate_profile_with_network failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def do_associate_dci_id_to_project(self, tenant):
        '''Associate DCI ID to Project'''

        context = {}
        args = json.dumps(tenant)
        try:
            resp = self.clnt.cast(context, 'associate_dci_id_to_project',
                                  msg=args)
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request to associate DCI_ID to Project failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_fabric_summary(self):
        '''Get fabric details from the Fabric Enabler'''

        context = {}
        args = json.dumps({})
        try:
            resp = self.clnt.call(context, 'get_fabric_summary', msg=args)
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for Fabric Summary failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_per_config_profile_detail(self, cfg_profile):
        '''Get all config Profiles details from the Fabric Enabler'''

        context = {}
        args = json.dumps(cfg_profile)
        try:
            resp = self.clnt.call(context, 'get_per_config_profile_detail',
                                  msg=args)
            return resp
        except Exception as e:
            mess = (_('%(reason)s') % {"reason": e})
            LOG.error(mess)
            reason = mess.partition("Traceback")[0]
            raise exceptions.NotAvailable(reason)

    def get_config_profiles_detail(self):
        '''Get all config Profiles details from the Fabric Enabler'''

        context = {}
        args = json.dumps({})
        try:
            resp = self.clnt.call(context, 'get_config_profiles_detail',
                                  msg=args)
            return resp
        except Exception as e:
            mess = (_('%(reason)s') % {"reason": e})
            reason = mess.partition("Traceback")[0]
            raise exceptions.NotAvailable(reason)

    def get_project_details(self, tenant):
        '''Get project details for a tenant from the Fabric Enabler'''

        context = {}
        args = json.dumps(tenant)
        try:
            resp = self.clnt.call(context, 'get_project_detail', msg=args)
            if not resp:
                raise exceptions.NotFound("Project Not Found in Fabric \
                                          Enabler")
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for project details failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_network_by_tenant_id(self, tenant):
        '''Get all networks for a tenant from the Fabric Enabler'''

        context = {}
        args = json.dumps(tenant)
        try:
            resp = self.clnt.call(context, 'get_all_networks_for_tenant',
                                  msg=args)
            if resp is False:
                raise exceptions.NotFound("Project Not Found in Fabric \
                                          Enabler")
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for project details failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_instance_by_tenant_id(self, tenant):
        '''Get all instances for a tenant from the Fabric Enabler'''

        context = {}
        args = json.dumps(tenant)
        try:
            resp = self.clnt.call(context, 'get_instance_by_tenant_id',
                                  msg=args)
            if resp is False:
                raise exceptions.NotFound("Project Not Found in Fabric \
                                          Enabler")
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for project details failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_agents_details(self):
        '''Get all Enabler agents from the Fabric Enabler'''

        context = {}
        args = json.dumps({})
        try:
            resp = self.clnt.call(context, 'get_agents_details', msg=args)
            if not resp:
                raise exceptions.NotFound("No Agents found for Fabric Enabler")
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for project details failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")

    def get_agent_details_per_host(self, agent):
        '''Get Enabler agent for a host from the Fabric Enabler'''

        context = {}
        args = json.dumps(agent)
        try:
            resp = self.clnt.call(context, 'get_agent_details_per_host',
                                  msg=args)
            if not resp:
                raise exceptions.NotFound("No Agent found for Fabric Enabler")
            return resp
        except (messaging.MessagingException, messaging.RemoteError,
                messaging.MessagingTimeout):
            LOG.error("RPC: Request for project details failed.")
            raise exceptions.NotAvailable("RPC to Fabric Enabler failed")
