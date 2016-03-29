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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from horizon_cisco_ui import api
from horizon_cisco_ui.cisco.asr1k import tables as asr1k_tables
from horizon_cisco_ui.cisco.asr1k.hosting_devices import tabs\
    as hosting_devices_tabs
from horizon_cisco_ui.cisco.asr1k.hosting_device_templates import tabs\
    as hosting_device_templates_tabs


class RouterTypesTab(tabs.TableTab):
    name = _("Router Types")
    slug = "router_types"
    table_classes = (asr1k_tables.RouterTypesTable,)
    template_name = 'horizon/common/_detail_table.html'

    def get_router_types_data(self):
        router_types = []
        request = self.tab_group.request
        try:
            router_types = api.router_type_list(request)
        except:
            exceptions.handle(request, _("Unable to retrieve Router Types"))
        return router_types


class IndexTabs(tabs.TabGroup):
    slug = "asr1k_tabs"
    tabs = (RouterTypesTab,
            hosting_devices_tabs.IndexTab,
            hosting_device_templates_tabs.IndexTab)
