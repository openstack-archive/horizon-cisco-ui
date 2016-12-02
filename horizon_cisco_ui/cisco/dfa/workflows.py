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

from django.utils.translation import ugettext_lazy as _

import logging

from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon_cisco_ui.cisco.dfa import dfa_client

from openstack_dashboard.dashboards.project.networks import \
    workflows as upstream_networks_workflows

LOG = logging.getLogger(__name__)


class DFAConfigProfileAction(workflows.Action):
    cfg_profile = forms.ChoiceField(label=_("Network Profile"), required=False,
                                    help_text=_("Select network profile to "
                                                "associate with Network."))

    class Meta(object):
        name = _("Programmable Fabric")

    ''' This function call get_config_profiles_detail api of DFA Client
        which fetches the profile list from Fabric Enabler using RPC,
        and return profile names filtered by the profile Sub Type

        p is an iterator over profile list that we got from the API
        q is a filtered list of profileNames based on the condition
    '''
    def _get_cfg_profiles(self, request):
        profiles = []
        try:
            dfaclient = dfa_client.DFAClient()
            if not bool(dfaclient.__dict__):
                return profiles
            cfgplist = dfaclient.get_config_profiles_detail()
            profiles = [q for p in cfgplist
                        if (p.get('profileSubType') == 'network:universal')
                        for q in [p.get('profileName')]]
        except Exception as exc:
            exceptions.handle(request, exc.message)
        return profiles

    def populate_cfg_profile_choices(self, request, context):
        profile_choices = [('', _("Select a config profile"))]
        for profile in self._get_cfg_profiles(request):
            profile_choices.append((profile, profile))
        return profile_choices

    def get_help_text(self, extra_context=None):
        text = ("Network Profile:"
                " An autoconfiguration template consisting of collection of"
                " commands which instantiates day-1 tenant-related"
                " configurations on CISCO Nexus switches.")
        return text


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
    def handle(self, request, data):
        network = self._create_network(request, data)
        if not network:
            return False
        if data['cfg_profile']:
            dfaclient = dfa_client.DFAClient()
            associate_data = {'id': network['id'],
                              'cfgp': data['cfg_profile'],
                              'name': network['name'],
                              'tenant_id': request.user.project_id}
            dfaclient.associate_profile_with_network(associate_data)
        # If we do not need to create a subnet, return here.
        if not data['with_subnet']:
            return True
        subnet = self._create_subnet(request, data, network, no_redirect=True)
        if subnet:
            return True
        else:
            self._delete_network(request, network)
            return False
