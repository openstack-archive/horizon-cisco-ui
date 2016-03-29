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

from django.core.urlresolvers import reverse_lazy
from openstack_dashboard.dashboards.project.routers \
    import tables as routers_tables


class CreateRouter(routers_tables.CreateRouter):
    url = "horizon:cisco:router_types:routers:create"

    def get_link_url(self, datum):
        router_type_id = self.table.get_object_id(datum)
        return reverse_lazy(self.url, args=(router_type_id,))
