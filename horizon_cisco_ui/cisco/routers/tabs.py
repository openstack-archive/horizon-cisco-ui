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
from openstack_dashboard.dashboards.admin.routers\
    import tabs as routers_tabs
from openstack_dashboard.dashboards.project.routers.extensions.routerrules\
    import tabs as rr_tabs


class OverviewTab(routers_tabs.OverviewTab):
    template_name = 'cisco/routers/overview_tab.html'


class DetailsTabs(routers_tabs.RouterDetailTabs):
    tabs = (OverviewTab,
            routers_tabs.InterfacesTab,
            routers_tabs.ExtraRoutesTab,
            rr_tabs.RulesGridTab,
            rr_tabs.RouterRulesTab)
