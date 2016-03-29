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

from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tabs

from horizon_cisco_ui import api
from horizon_cisco_ui.cisco.router_types import tables

from openstack_dashboard.api import neutron
from openstack_dashboard.dashboards.project.routers \
    import tables as routers_tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = 'overview'
    template_name = 'cisco/router_types/overview_tab.html'

    def get_context_data(self, request):
        router_type = self.tab_group.kwargs['router_type']
        context = { 'router_type': router_type }
        template_detail_url = \
            'horizon:cisco:device_management:hosting_device_templates:details'
        context["device_template_url"] = \
            reverse(template_detail_url, args=(router_type.template_id,) )
        return context


class RoutersTab(tabs.TableTab):
    name = _("Routers")
    slug = "routers"
    table_classes = (routers_tables.RoutersTable,)
    template_name = 'horizon/common/_detail_table.html'

    def get_routers_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            router_type = self.tab_group.kwargs['router_type']
            routers = neutron.router_list(self.request,
                                          tenant_id=tenant_id)
            
            ext_net_dict = self._list_external_networks()
            for r in routers:
                r.name = r.name_or_id
                self._set_external_network(r, ext_net_dict)
            
            return [router for router in routers
                    if router.routertype__id == router_type.id]
        except Exception:
            routers = []
            exceptions.handle(self.request,
                              _('Unable to retrieve router list.'))
        return routers

    def _list_external_networks(self):
        try:
            search_opts = {'router:external': True}
            ext_nets = neutron.network_list(self.request,
                                                **search_opts)
            ext_net_dict = OrderedDict((n['id'], n.name_or_id)
                                       for n in ext_nets)
        except Exception as e:
            msg = _('Unable to retrieve a list of external networks "%s".') % e
            exceptions.handle(self.request, msg)
            ext_net_dict = {}
        return ext_net_dict

    def _set_external_network(self, router, ext_net_dict):
        gateway_info = router.external_gateway_info
        if gateway_info:
            ext_net_id = gateway_info['network_id']
            if ext_net_id in ext_net_dict:
                gateway_info['network'] = ext_net_dict[ext_net_id]
            else:
                msg_params = {'ext_net_id': ext_net_id, 'router_id': router.id}
                msg = _('External network "%(ext_net_id)s" expected but not '
                        'found for router "%(router_id)s".') % msg_params
                messages.error(self.request, msg)
                # gateway_info['network'] is just the network name, so putting
                # in a smallish error message in the table is reasonable.
                # Translators: The usage is "<UUID of ext_net> (Not Found)"
                gateway_info['network'] = pgettext_lazy(
                    'External network not found',
                    u'%s (Not Found)') % ext_net_id


class DetailsTabs(tabs.TabGroup):
    slug = 'router_types_details_tabs'
    tabs = (OverviewTab, RoutersTab)
