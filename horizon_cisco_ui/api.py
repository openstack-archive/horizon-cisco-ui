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


from neutronclient.v2_0 import client

from openstack_dashboard.api import neutron


class RouterType(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Router Type resources """


class HostingDevice(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Hosting Device resources """


class HostingDeviceTemplate(neutron.NeutronAPIDictWrapper):
    """ Wrapper for Cisco Hosting Device Template resources """


def router_type_show(request, type_id, **params):
    router_type = neutron.neutronclient(request)\
        .show_routertype(type_id, **params).get('routertype')
    return RouterType(router_type)


def router_type_list(request, **params):
    router_types = neutron.neutronclient(request).list_routertypes(**params)\
        .get('routertypes')
    return [RouterType(r) for r in router_types]


def hosting_device_delete(request, device_id):
    hosting_device = neutron.neutronclient(request)\
        .delete_hosting_device(device_id)


def hosting_device_show(request, device_id, **params):
    hosting_device = neutron.neutronclient(request)\
        .show_hosting_device(device_id, **params).get('hosting_device')
    return HostingDevice(hosting_device)


def hosting_device_list(request, **params):
    hosting_devices = neutron.neutronclient(request)\
        .list_hosting_devices(**params).get('hosting_devices')
    return [HostingDevice(device) for device in hosting_devices]


def hosting_device_template_delete(request, device_id):
    hosting_device_template = neutron.neutronclient(request)\
        .delete_hosting_device_template(template_id)


def hosting_device_template_show(request, template_id, **params):
    hosting_device_template = neutron.neutronclient(request)\
        .show_hosting_device_template(template_id, **params)\
            .get('hosting_device_template')
    return HostingDeviceTemplate(hosting_device_template)


def hosting_device_template_list(request, **params):
    hosting_device_templates = neutron.neutronclient(request)\
        .list_hosting_device_templates(**params)\
            .get('hosting_device_templates')
    return [HostingDeviceTemplate(tmplt) for tmplt in hosting_device_templates]
