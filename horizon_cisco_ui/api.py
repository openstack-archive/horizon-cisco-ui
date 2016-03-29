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


from neutronclient.v2_0 import client

from openstack_dashboard.api import neutron


class RouterType(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Router Type resources """


class HostingDevice(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Hosting Device resources """


class HostingDeviceTemplate(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Hosting Device Template resources """


def router_type_list(request, **params):
    routertypes = neutron.neutronclient(request).list_routertypes(**params)\
        .get('routertypes')
    return [RouterType(r) for r in routertypes]


def hosting_device_list(request, **params):
    hosting_devices = neutron.neutronclient(request)\
            .list_hosting_devices(**params).get('hosting_devices')
    return [HostingDevice(device) for device in hosting_devices]


def hosting_device_template_list(request, **params):
    hosting_device_templates = neutron.neutronclient(request)\
            .list_hosting_device_templates(**params)\
            .get('hosting_device_templates')
    return [HostingDeviceTemplate(tmplt) for tmplt in hosting_device_templates]
