# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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


from django.utils.text import normalize_newlines  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances.workflows import \
    create_instance as upstream_create_instance

LOG = logging.getLogger(__name__)


class N1KvSetNetworkAction(upstream_create_instance.SetNetworkAction):

    if api.neutron.is_port_profiles_supported():
        widget = None
    else:
        widget = forms.HiddenInput()
    profile = forms.ChoiceField(label=_("Policy Profiles"),
                                required=False,
                                widget=widget,
                                help_text=_("Launch instance with "
                                            "this policy profile"))

    def __init__(self, request, *args, **kwargs):
        super(N1KvSetNetworkAction, self).__init__(request, *args, **kwargs)
        if api.neutron.is_port_profiles_supported():
            self.fields['profile'].choices = (
                self.get_policy_profile_choices(request))

    def get_policy_profile_choices(self, request):
        profile_choices = [('', _("Select a profile"))]
        for profile in self._get_profiles(request, 'policy'):
            profile_choices.append((profile.id, profile.name))
        return profile_choices

    def _get_profiles(self, request, type_p):
        profiles = []
        try:
            profiles = api.neutron.profile_list(request, type_p)
        except Exception:
            msg = _('Network Profiles could not be retrieved.')
            exceptions.handle(request, msg)
        return profiles

    class Meta(object):
        name = _("Networking")
        permissions = ('openstack.services.network',)
        help_text = _("Select networks for your instance.")


class N1KvSetNetwork(upstream_create_instance.SetNetwork):
    action_class = N1KvSetNetworkAction
    # Disabling the template drag/drop only in the case port profiles
    # are used till the issue with the drag/drop affecting the
    # profile_id detection is fixed.
    if api.neutron.is_port_profiles_supported():
        contributes = ("network_id", "profile_id",)
        template_name = "horizon/common/_workflow_step.html"
    else:
        template_name = "project/instances/_update_networks.html"
        contributes = ("network_id",)

    def contribute(self, data, context):
        if data:
            networks = self.workflow.request.POST.getlist("network")
            # If no networks are explicitly specified, network list
            # contains an empty string, so remove it.
            networks = [n for n in networks if n != '']
            if networks:
                context['network_id'] = networks

            if api.neutron.is_port_profiles_supported():
                context['profile_id'] = data.get('profile', None)
        return context


class LaunchInstance(upstream_create_instance.LaunchInstance):

    default_steps = (upstream_create_instance.SelectProjectUser,
                     upstream_create_instance.SetInstanceDetails,
                     upstream_create_instance.SetAccessControls,
                     N1KvSetNetwork,
                     upstream_create_instance.PostCreationStep,
                     upstream_create_instance.SetAdvanced)

    def format_status_message(self, message):
        name = self.context.get('name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s instances") % count,
                              "name": name}
        else:
            return message % {"count": _("instance"), "name": name}

    @staticmethod
    @sensitive_variables('context')
    def handle(self, request, context):
        def set_network_port_profiles(request, net_ids, profile_id):
            # Create port with Network ID and Port Profile
            # for the use with the plugin supporting port profiles.
            nics = []
            for net_id in net_ids:
                try:
                    port = api.neutron.port_create(
                        request,
                        net_id,
                        policy_profile_id=profile_id,
                    )
                except Exception as e:
                    msg = (_('Unable to create port for profile '
                             '"%(profile_id)s": %(reason)s'),
                           {'profile_id': profile_id,
                            'reason': e})
                    for nic in nics:
                        try:
                            port_id = nic['port-id']
                            api.neutron.port_delete(request, port_id)
                        except Exception:
                            msg = (msg +
                                   _(' Also failed to delete port %s') %
                                   port_id)
                    redirect = self.success_url
                    exceptions.handle(request, msg, redirect=redirect)

                if port:
                    nics.append({"port-id": port.id})
                    LOG.debug("Created Port %(portid)s with "
                              "network %(netid)s "
                              "policy profile %(profile_id)s",
                              {'portid': port.id,
                               'netid': net_id,
                               'profile_id': profile_id})

            return nics

        custom_script = context.get('script_data', '')

        dev_mapping_1 = None
        dev_mapping_2 = None

        image_id = ''

        # Determine volume mapping options
        source_type = context.get('source_type', None)
        if source_type in ['image_id', 'instance_snapshot_id']:
            image_id = context['source_id']
        elif source_type in ['volume_id', 'volume_snapshot_id']:
            try:
                if api.nova.extension_supported("BlockDeviceMappingV2Boot",
                                                request):
                    # Volume source id is extracted from the source
                    volume_source_id = context['source_id'].split(':')[0]
                    device_name = context.get('device_name', '') \
                        .strip() or None
                    dev_mapping_2 = [
                        {'device_name': device_name,
                         'source_type': 'volume',
                         'destination_type': 'volume',
                         'delete_on_termination':
                             int(bool(context['delete_on_terminate'])),
                         'uuid': volume_source_id,
                         'boot_index': '0',
                         'volume_size': context['volume_size']
                         }
                    ]
                else:
                    dev_mapping_1 = {context['device_name']: '%s::%s' %
                                     (context['source_id'],
                                     int(bool(context['delete_on_terminate'])))
                                     }
            except Exception:
                msg = _('Unable to retrieve extensions information')
                exceptions.handle(request, msg)

        elif source_type == 'volume_image_id':
            device_name = context.get('device_name', '').strip() or None
            dev_mapping_2 = [
                {'device_name': device_name,  # None auto-selects device
                 'source_type': 'image',
                 'destination_type': 'volume',
                 'delete_on_termination':
                     int(bool(context['delete_on_terminate'])),
                 'uuid': context['source_id'],
                 'boot_index': '0',
                 'volume_size': context['volume_size']
                 }
            ]

        netids = context.get('network_id', None)
        if netids:
            nics = [{"net-id": netid, "v4-fixed-ip": ""}
                    for netid in netids]
        else:
            nics = None

        avail_zone = context.get('availability_zone', None)

        port_profiles_supported = api.neutron.is_port_profiles_supported()
        if port_profiles_supported:
            nics = set_network_port_profiles(request,
                                             context['network_id'],
                                             context['profile_id'],)
        try:
            api.nova.server_create(request,
                                   context['name'],
                                   image_id,
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   context['security_group_ids'],
                                   block_device_mapping=dev_mapping_1,
                                   block_device_mapping_v2=dev_mapping_2,
                                   nics=nics,
                                   availability_zone=avail_zone,
                                   instance_count=int(context['count']),
                                   admin_pass=context['admin_pass'],
                                   disk_config=context.get('disk_config'),
                                   config_drive=context.get('config_drive'))
            return True
        except Exception:
            if port_profiles_supported:
                ports_failing_deletes = _cleanup_ports_on_failed_vm_launch(
                    request, nics)
                if ports_failing_deletes:
                    ports_str = ', '.join(ports_failing_deletes)
                    msg = (_('Port cleanup failed for these port-ids (%s).')
                           % ports_str)
                    exceptions.handle(request, msg)
            exceptions.handle(request)
        return False


def _cleanup_ports_on_failed_vm_launch(request, nics):
    ports_failing_deletes = []
    LOG.debug('Cleaning up stale VM ports.')
    for nic in nics:
        try:
            LOG.debug('Deleting port with id: %s' % nic['port-id'])
            api.neutron.port_delete(request, nic['port-id'])
        except Exception:
            ports_failing_deletes.append(nic['port-id'])
    return ports_failing_deletes
