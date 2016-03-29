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
from horizon_cisco_ui.cisco.device_management.hosting_device_templates \
    import tables


class IndexTab(tabs.TableTab):
    name = _("Hosting Device Templates")
    slug = "hosting_device_templates"
    table_classes = (tables.HostingDeviceTemplatesTable,)
    template_name = 'horizon/common/_detail_table.html'

    def get_hosting_device_templates_data(self):
        hosting_device_templates = []
        request = self.tab_group.request
        try:
            hosting_device_templates = api.hosting_device_template_list(request)
        except:
            exceptions.handle(request, _("Unable to retrieve Hosting Device Templates"))
        return hosting_device_templates


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = 'overview'
    template_name = \
        'cisco/device_management/hosting_device_templates/overview_tab.html'

    def get_context_data(self, request):
        return { 'device_template': self.tab_group.kwargs['device_template'] }


class DetailsTabs(tabs.TabGroup):
    slug = 'hosting_device_templates_details_tabs'
    tabs = (OverviewTab, )
