# Copyright 2016 Cisco Systems, Inc.
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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.routers \
    import forms as routers_forms

LOG = logging.getLogger(__name__)


class CreateForm(routers_forms.CreateForm):
    failure_url = "horizon:cisco:router_types:index"
    router_type_id = forms.CharField(label=_("Router Type ID"),
                                     required=False,
                                     widget=forms.TextInput(
                                         attrs={'readonly': 'readonly'}))
    router_type_name = forms.CharField(label=_("Router Type Name"),
                                       required=False,
                                       widget=forms.TextInput(
                                           attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                    'routertype:id': data['router_type_id']}
            if 'admin_state_up' in data and data['admin_state_up']:
                params['admin_state_up'] = data['admin_state_up']
            if (self.dvr_allowed and data['mode'] != 'server_default'):
                params['distributed'] = (data['mode'] == 'distributed')
            if (self.ha_allowed and data['ha'] != 'server_default'):
                params['ha'] = (data['ha'] == 'enabled')
            router = api.neutron.router_create(request, **params)
        except Exception as exc:
            if hasattr(exc, 'status_code') and exc.status_code == 409:
                msg = _('Quota exceeded for resource router.')
            else:
                msg = _('Failed to create router "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False

        # workaround for neutron bug #1535707
        try:
            if ('external_network' in data and
                    data['external_network']):
                api.neutron.router_add_gateway(request,
                                               router['id'],
                                               data['external_network'])
            message = _('Router %s was successfully created.') % data['name']
            messages.success(request, message)
            return router
        except Exception:
            try:
                api.neutron.router_delete(request, router['id'])
                message = _('Router %s was created but connecting to'
                            ' an external network failed. The created'
                            ' router has been deleted, as the overall'
                            ' operation failed.') % data['name']
                LOG.info(message)
                redirect = reverse(self.failure_url)
                exceptions.handle(request, message, redirect=redirect)
                return False
            except Exception:
                message = _('Router %(name)s was created but connecting to'
                            ' an external network failed. Attempts to'
                            ' delete the new router also failed.'
                            ' Router %(name)s still exists but is not connect'
                            ' to the desired external network.') % {
                    'name': data['name']}
                LOG.info(message)
                redirect = reverse(self.failure_url)
                exceptions.handle(request, message, redirect=redirect)
                return False
