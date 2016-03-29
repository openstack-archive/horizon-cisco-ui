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

from django.conf.urls import include
from django.conf.urls import url

from horizon_cisco_ui.cisco.device_management import views
from horizon_cisco_ui.cisco.device_management.hosting_devices \
    import urls as hosting_devices_urls
from horizon_cisco_ui.cisco.device_management.hosting_device_templates \
    import urls as hosting_device_templates_urls

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^\?tab=device_management_tabs__hosting_devices$',
        views.IndexView.as_view(), name='hosting_devices'),
    url(r'hosting_devices/', include(hosting_devices_urls,
        namespace='hosting_devices')),
    url(r'^\?tab=device_management_tabs__hosting_device_templates$',
        views.IndexView.as_view(), name='hosting_device_templates'),
    url(r'hosting_device_templates/',
        include(hosting_device_templates_urls,
        namespace='hosting_device_templates')),
]
