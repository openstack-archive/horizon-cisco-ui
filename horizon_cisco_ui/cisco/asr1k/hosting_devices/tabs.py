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
from horizon_cisco_ui.cisco.asr1k.hosting_devices import tables


class IndexTab(tabs.TableTab):
    name = _("Hosting Devices")
    slug = "hosting_devices"
    table_classes = (tables.HostingDevicesTable,)
    template_name = 'horizon/common/_detail_table.html'

    def get_hosting_devices_data(self):
        hosting_devices = []
        request = self.tab_group.request
        try:
            hosting_devices = api.hosting_device_list(request)
        except:
            exceptions.handle(request, _("Unable to retrieve Hosting Devices"))
        return hosting_devices


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = 'overview'
    template_name = 'cisco/asr1k/hosting_devices/overview_tab.html'

    def get_context_data(self, request):
        return { 'hosting_device': self.tab_group.kwargs['hosting_device'] }


class DetailsTabs(tabs.TabGroup):
    slug = 'hosting_devices_details_tabs'
    tabs = (OverviewTab, )
