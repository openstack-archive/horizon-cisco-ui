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


from horizon_cisco_ui.firewalls \
    import views as cisco_firewall_views
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.firewalls \
    import views as firewall_views

from horizon_cisco_ui.dashboards.project.instances.workflows import \
    create_instance as cisco_create_instance
from openstack_dashboard.dashboards.project.instances.workflows import \
    create_instance as upstream_create_instance


if api.neutron.is_port_profiles_supported():
    upstream_create_instance.LaunchInstance.handle = \
        cisco_create_instance.N1KvLaunchInstance.handle
    upstream_create_instance.LaunchInstance.default_steps = \
        cisco_create_instance.N1KvLaunchInstance.default_steps

# TODO(robcresswell): remove example
# Silly example that does nothing, but illustrates an override.
firewall_views.IndexView = cisco_firewall_views.IndexView
