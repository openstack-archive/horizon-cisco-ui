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


# The slug of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'cisco'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'horizon_cisco_ui.cisco',
    'horizon_cisco_ui.firewalls',
]

# Extra values to add to the Horizon settings
UPDATE_HORIZON_CONFIG = {
    'customization_module': 'horizon_cisco_ui.overrides',
}
