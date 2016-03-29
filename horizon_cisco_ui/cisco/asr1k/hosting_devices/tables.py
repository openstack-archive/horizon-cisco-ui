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


class HostingDevicesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"),
                       link="horizon:cisco:asr1k:hosting_devices:details")
    name = tables.Column('name', verbose_name=_("Name"))
    template_id = tables.Column('template_id', verbose_name=_("Template ID"))
    admin_state_up = tables.Column('admin_state_up', verbose_name=_("Admin State"))
    status = tables.Column('status', verbose_name=_("Status"))

    class Meta(object):
        name = "hosting_devices"
        verbose_name = _("Hosting Devices")
