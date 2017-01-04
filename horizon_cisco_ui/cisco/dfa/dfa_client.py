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
    """Represents Nexus Fabric Enabler RPC Client."""

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


@memoized
def dfaclient():
    return DFAClient().clnt


def associate_profile_with_network(network):
    '''Associate Network Profile with network'''

    try:
        resp = dfaclient().call({}, 'associate_profile_with_network',
                                msg=network)
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request to associate_profile_with_network failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def do_associate_dci_id_to_project(tenant):
    '''Associate DCI ID to Project'''

    try:
        resp = dfaclient().cast({}, 'associate_dci_id_to_project',
                                msg=tenant)
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request to associate DCI_ID to Project failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_fabric_summary():
    '''Get fabric details from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_fabric_summary', msg={})
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for Fabric Summary failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_per_config_profile_detail(cfg_profile):
    '''Get all config Profiles details from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_per_config_profile_detail',
                                msg=cfg_profile)
        return resp
    except Exception as e:
        mess = (_('%(reason)s') % {"reason": e})
        LOG.error(mess)
        reason = mess.partition("Traceback")[0]
        raise exceptions.NotAvailable(reason)


def get_config_profiles_detail():
    '''Get all config Profiles details from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_config_profiles_detail', msg={})
        return resp
    except Exception as e:
        mess = (_('%(reason)s') % {"reason": e})
        reason = mess.partition("Traceback")[0]
        raise exceptions.NotAvailable(reason)


def get_project_details(tenant):
    '''Get project details for a tenant from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_project_detail', msg=tenant)
        if not resp:
            raise exceptions.NotFound("Project Not Found in Fabric \
                                      Enabler")
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for project details failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_network_by_tenant_id(tenant):
    '''Get all networks for a tenant from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_all_networks_for_tenant', msg=tenant)
        if resp is False:
            raise exceptions.NotFound("Project Not Found in Fabric \
                                      Enabler")
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for project details failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_instance_by_tenant_id(tenant):
    '''Get all instances for a tenant from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_instance_by_tenant_id', msg=tenant)
        if resp is False:
            raise exceptions.NotFound("Project Not Found in Fabric \
                                      Enabler")
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for project details failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_agents_details():
    '''Get all Enabler agents from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_agents_details', msg={})
        if not resp:
            raise exceptions.NotFound("No Agents found for Fabric Enabler")
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for project details failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")


def get_agent_details_per_host(agent):
    '''Get Enabler agent for a host from the Fabric Enabler'''

    try:
        resp = dfaclient().call({}, 'get_agent_details_per_host', msg=agent)
        if not resp:
            raise exceptions.NotFound("No Agent found for Fabric Enabler")
        return resp
    except (messaging.MessagingException, messaging.RemoteError,
            messaging.MessagingTimeout):
        LOG.error("RPC: Request for project details failed.")
        raise exceptions.NotAvailable("RPC to Fabric Enabler failed")
