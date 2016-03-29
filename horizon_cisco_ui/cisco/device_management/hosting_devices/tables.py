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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables
from horizon_cisco_ui import api

LOG = logging.getLogger(__name__)


class DeleteHostingDevice(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Hosting Device",
            u"Delete Hosting Devices",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Hosting Device",
            u"Deleted Hosting Devices",
            count
        )

    def delete(self, request, obj_id):
        try:
            api.hosting_device_delete(request, obj_id)
        except Exception as e:
            LOG.info(e)
            redirect = reverse('horizon:cisco:device_management:index')
            exceptions.handle(request, e, redirect=redirect)


class HostingDevicesTable(tables.DataTable):
    id = tables.Column(
        'id', verbose_name=_("ID"),
        link="horizon:cisco:device_management:hosting_devices:details")
    name = tables.Column('name', verbose_name=_("Name"))
    template_id = tables.Column(
        'template_id', verbose_name=_("Template ID"),
        link="horizon:cisco:device_management:hosting_device_templates:details"
    )
    admin_state_up = tables.Column('admin_state_up',
                                   verbose_name=_("Admin State Up"))
    status = tables.Column('status', verbose_name=_("Status"))

    class Meta(object):
        name = "hosting_devices"
        verbose_name = _("Hosting Devices")
        table_actions = (DeleteHostingDevice,)
        row_actions = (DeleteHostingDevice,)
