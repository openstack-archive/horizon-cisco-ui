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

from django.core.urlresolvers import reverse
from django import http
from horizon_cisco_ui import api
from horizon_cisco_ui.test import helpers
from mox3.mox import IsA
from openstack_dashboard.test import helpers as test

INDEX_URL = reverse('horizon:cisco:device_management:hosting_devices')


class HostingDevicesTest(helpers.AdminTestCase):
    @test.create_stubs({api: ['hosting_device_list',
                              'hosting_device_template_list']})
    def test_index_view(self):
        # Get test data
        hosting_devices = self.hosting_devices.list()
        hosting_device_templates = self.hosting_device_templates.list()

        # Expected API calls
        api.hosting_device_list(IsA(http.HttpRequest))\
            .AndReturn(hosting_devices)
        api.hosting_device_template_list(IsA(http.HttpRequest))\
            .AndReturn(hosting_device_templates)

        # Assertions
        self.mox.ReplayAll()
        self.assertTemplateUsed(
            self.client.get(INDEX_URL), 'cisco/device_management/index.html'
        )
        self.mox.VerifyAll()
