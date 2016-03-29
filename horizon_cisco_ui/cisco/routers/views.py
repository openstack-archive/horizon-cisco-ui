# Copyright 2015 Cisco Systems, Inc.
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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from horizon_cisco_ui import api
from horizon_cisco_ui.cisco.routers import tables as routers_tables
from horizon_cisco_ui.cisco.routers import tabs as routers_tabs

from openstack_dashboard.dashboards.admin.routers \
    import views as routers_views


class IndexView(routers_views.IndexView):
    table_class = routers_tables.IndexTable
    template_name = 'cisco/router_types/index.html'


class DetailView(routers_views.DetailView):
    tab_group_class = routers_tabs.DetailsTabs
    template_name = 'horizon/common/_detail.html'
