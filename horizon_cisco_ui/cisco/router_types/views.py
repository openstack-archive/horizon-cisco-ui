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
from horizon_cisco_ui.cisco.router_types import tables as router_types_tables
from horizon_cisco_ui.cisco.router_types import tabs as router_types_tabs


class IndexView(tables.DataTableView):
    table_class = router_types_tables.IndexTable
    template_name = 'cisco/router_types/index.html'
    page_title = _("Router Types")

    def get_data(self):
        router_types = []
        try:
            router_types = api.router_type_list(self.request)
        except:
            msg = _("Unable to retrieve Router Types")
            exceptions.handle(self.request, msg)
        return router_types


class DetailView(tabs.TabbedTableView):
    tab_group_class = router_types_tabs.DetailsTabs
    page_title = '{{ router_type_title }}'
    template_name = 'horizon/common/_detail.html'

    @memoized.memoized_method
    def _get_data(self):
        router_type_id = self.kwargs['router_type_id']
        try:
            router_type = api.router_type_show(self.request, router_type_id)
        except Exception:
            router_type = {}
            msg = \
                _("Unable to retrieve details for router type %s")\
                % template_id
            exceptions.handle(self.request, msg)
        return router_type

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        router_type = self._get_data()
        context["router_type_title"] = getattr(router_type, 'name', router_type.id)
        return context

    def get_tabs(self, request, *args, **kwargs):
        router_type = self._get_data()
        return self.tab_group_class(request,
                                    router_type=router_type,
                                    **kwargs)
