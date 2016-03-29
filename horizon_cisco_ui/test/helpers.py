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

from horizon_cisco_ui.test import test_data
from openstack_dashboard.test import helpers


class AdminTestCase(helpers.BaseAdminViewTests):
    """Extends the base Horizon AdminViewTests with Cisco UI data"""

    def _setup_test_data(self):
        super(AdminTestCase, self)._setup_test_data()
        test_data.data(self)


class APITestCase(helpers.APITestCase):
    """Extends the base Horizon APITestCase with Cisco UI data"""

    def _setup_test_data(self):
        super(APITestCase, self)._setup_test_data()
        test_data.data(self)
