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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon_cisco_ui.cisco.dfa import dfa_client

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.networks import \
    workflows as upstream_networks_workflows

LOG = logging.getLogger(__name__)


class DFAConfigProfileAction(workflows.Action):
    cfg_profile = forms.ChoiceField(label=_("Config Profile"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(DFAConfigProfileAction, self).__init__(request, *args, **kwargs)
        self.fields['cfg_profile'].choices = \
            self.get_config_profile_choices(request)

    def get_config_profile_choices(self, request):
        profile_choices = [('', _("Select a config profile"))]
        for profile in self._get_cfg_profiles(request):
            profile_choices.append((profile, profile))
        return profile_choices

    def _get_cfg_profiles(self, request):
        profiles = []
        try:
            dc = dfa_client.dfa_client()
            profiles = dc.get_all_config_profiles()
        except Exception as exc:
            exceptions.handle(request, exc.message)
        return profiles

    class Meta(object):
        name = _("DFA")
        help_text = _("Select Network Configuration Profile from the list "
                      "to associate with your network.")


class DFAConfigProfileInfo(workflows.Step):
    action_class = DFAConfigProfileAction

    def contribute(self, data, context):
        for k, v in data.items():
            context[k] = v
        return context


class DFACreateNetwork(upstream_networks_workflows.CreateNetwork):
    default_steps = (upstream_networks_workflows.CreateNetworkInfo,
                     upstream_networks_workflows.CreateSubnetInfo,
                     upstream_networks_workflows.CreateSubnetDetail,
                     DFAConfigProfileInfo)

    @staticmethod
    def _create_network(self, request, data):
        try:
            params = {'name': data['net_name'],
                      'admin_state_up': (data['admin_state'] == 'True'),
                      'shared': data['shared']}
            if api.neutron.is_port_profiles_supported():
                params['net_profile_id'] = data['net_profile_id']
            network = api.neutron.network_create(request, **params)
            self.context['net_id'] = network.id
            msg = (_('Network "%s" was successfully created.') %
                   network.name_or_id)
            LOG.debug(msg)
            return network
        except Exception as e:
            msg = (_('Failed to create network "%(network)s": %(reason)s') %
                   {"network": data['net_name'], "reason": e})
            LOG.info(msg)
            # Delete Precreated Network
            try:
                precreate_network = dict(tenant_id=request.user.project_id,
                                         nwk_name=data['net_name'],
                                         subnet=data['cidr'],
                                         cfgp=data['cfg_profile'])
                dc = dfa_client.dfa_client()
                dc.do_delete_precreate_network(precreate_network)
                precreate_flag = False
            except Exception as exc:
                LOG.error('Unable to do delete precreate Network')
                exceptions.handle(self.request, exc.message)
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)
            return False

    @staticmethod
    def handle(self, request, data):
        precreate_flag = False

        precreate_network = dict(tenant_id=request.user.project_id,
                                 nwk_name=data['net_name'],
                                 subnet=data['cidr'],
                                 cfgp=data['cfg_profile'])
        dc = dfa_client.dfa_client()
        if data['cfg_profile']:
            '''Pre-create network in enabler'''
            try:
                dc.do_precreate_network(precreate_network)
                precreate_flag = True
            except Exception as exc:
                LOG.error('Unable to do precreate Network')
                exceptions.handle(self.request, exc.message)
                return False

        network = self._create_network(request, data)
        if not network:
            if precreate_flag:
                # do precreate delete
                try:
                    dc.do_delete_precreate_network(precreate_network)
                    precreate_flag = False
                except Exception as exc:
                    LOG.error('Unable to do delete precreate Network')
                    exceptions.handle(self.request, exc.message)
            return False
        # If we do not need to create a subnet, return here.
        if not data['with_subnet']:
            return True
        subnet = self._create_subnet(request, data, network, no_redirect=True)
        if subnet:
            return True
        else:
            self._delete_network(request, network)
            if precreate_flag:
                # do precreate delete
                try:
                    dc.do_delete_precreate_network(precreate_network)
                    precreate_flag = False
                except Exception as exc:
                    LOG.error('Unable to do delete precreate Network')
                    exceptions.handle(self.request, exc.message)
            return False
