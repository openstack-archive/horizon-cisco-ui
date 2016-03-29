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

from django.utils.translation import ugettext_lazy as _

from horizon import tables

class RouterTypesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"))
    name = tables.Column('name', verbose_name=_("Name"))
    description = tables.Column('description', verbose_name=_("Description"))
    template_id = tables.Column('template_id', verbose_name=_("Template ID"))

    class Meta(object):
        name = "router_types"
        verbose_name = _("Router Types")


class HostingDevicesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"))
    name = tables.Column('name', verbose_name=_("Name"))
    template_id = tables.Column('template_id', verbose_name=_("Template ID"))
    admin_state_up = tables.Column('admin_state_up', verbose_name=_("Admin State"))
    status = tables.Column('status', verbose_name=_("Status"))
    
    class Meta(object):
        name = "hosting_devices"
        verbose_name = _("Hosting Devices")


class HostingDeviceTemplatesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"))
    name = tables.Column('name', verbose_name=_("Name"))
    host_category = tables.Column('host_category', verbose_name=_("Host Category"))
    service_types = tables.Column('service_types', verbose_name=_("Service Types"))
    enabled = tables.Column('enabled', verbose_name=_("Enabled"))

    class Meta(object):
        name = "hosting_device_templates"
        verbose_name = _("Hosting Device Templates")
