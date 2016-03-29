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

from horizon_cisco_ui import api
from openstack_dashboard.test.test_data import utils


def data(TEST):
    # Test Data Containers
    TEST.hosting_devices = utils.TestDataContainer()
    TEST.hosting_device_templates = utils.TestDataContainer()
    TEST.router_types = utils.TestDataContainer()

    # Hosting Devices
    hosting_device_1 = {
        "status": "ACTIVE",
        "protocol_port": 22,
        "description": "",
        "name": "",
        "admin_state_up": True,
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "auto_delete": False,
        "management_port_id": "",
        "id": "00000000-0000-0000-0000-000000000003",
        "cfg_agent_id": "951bbaf3-b8d8-4586-ad1b-27fdcba949bc",
        "tenant_bound": "",
        "management_ip_address": "10.30.119.41",
        "credentials_id": "00000000-0000-0000-0000-000000000001",
        "created_at": "2016-06-09 17:58:30",
        "template_id": "00000000-0000-0000-0000-000000000003",
        "device_id": "SN:abcd1234efgh"
    }

    hosting_device_2 = {
        "status": "ACTIVE",
        "protocol_port": 22,
        "description": "",
        "name": "",
        "admin_state_up": True,
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "auto_delete": False,
        "management_port_id": "",
        "id": "00000000-0000-0000-0000-000000000004",
        "cfg_agent_id": "951bbaf3-b8d8-4586-ad1b-27fdcba949bc",
        "tenant_bound": "",
        "management_ip_address": "10.30.119.42",
        "credentials_id": "00000000-0000-0000-0000-000000000001",
        "created_at": "2016-06-09 17:58:30",
        "template_id": "00000000-0000-0000-0000-000000000003",
        "device_id": "SN:efgh5678ijkl"
    }

    TEST.hosting_devices.add(api.HostingDevice(hosting_device_1))
    TEST.hosting_devices.add(api.HostingDevice(hosting_device_2))

    # Hosting Device Templates
    hosting_device_template_1 = {
        "service_types": "router:FW:VPN",
        "slot_capacity": 2000,
        "name": "NetworkNode",
        "configuration_mechanism": "",
        "booting_time": 360,
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "image": "",
        "desired_slots_free": 0,
        "enabled": True,
        "default_credentials_id": "00000000-0000-0000-0000-000000000001",
        "id": "00000000-0000-0000-0000-000000000001",
        "host_category": "Network_Node",
        "plugging_driver": "noop_plugging_driver.NoopPluggingDriver",
        "device_driver": "noop_hd_driver.NoopHostingDeviceDriver",
        "protocol_port": 22,
        "flavor": "",
        "tenant_bound": ""
    }

    hosting_device_template_2 = {
        "service_types": "router:FW:VPN",
        "slot_capacity": 2000,
        "name": "CSR1kv template",
        "configuration_mechanism": "",
        "booting_time": 360,
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "image": "csr1kv_openstack_img",
        "desired_slots_free": 0,
        "enabled": True,
        "default_credentials_id": "00000000-0000-0000-0000-000000000001",
        "id": "00000000-0000-0000-0000-000000000002",
        "host_category": "Hardware",
        "plugging_driver": "N1kvML2TrunkingPlugDriver",
        "device_driver": "csr1kv_hd_driver.CSR1kvHostingDeviceDriver",
        "protocol_port": 22,
        "flavor": "621",
        "tenant_bound": ""
    }

    hosting_device_template_3 = {
        "service_types": "router:FW:VPN",
        "slot_capacity": 2000,
        "name": "ASR1k template",
        "configuration_mechanism": "",
        "booting_time": 360,
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "image": "",
        "desired_slots_free": 0,
        "enabled": True,
        "default_credentials_id": "00000000-0000-0000-0000-000000000001",
        "id": "00000000-0000-0000-0000-000000000003",
        "host_category": "Hardware",
        "plugging_driver": "hw_vlan_trunking_driver.HwVLANTrunkingPlugDriver",
        "device_driver": "noop_hd_driver.NoopHostingDeviceDriver",
        "protocol_port": 22,
        "flavor": "",
        "tenant_bound": ""
    }

    TEST.hosting_device_templates.add(
        api.HostingDeviceTemplate(hosting_device_template_1)
    )
    TEST.hosting_device_templates.add(
        api.HostingDeviceTemplate(hosting_device_template_2)
    )
    TEST.hosting_device_templates.add(
        api.HostingDeviceTemplate(hosting_device_template_3)
    )

    # Router Types
    router_type_1 = {
        "slot_need": 0,
        "description": "Neutron router implemented in Linux network namespace",
        "template_id": "00000000-0000-0000-0000-000000000001",
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "ha_enabled_by_default": False,
        "driver": "",
        "cfg_agent_driver": "",
        "scheduler": "",
        "shared": True,
        "cfg_agent_service_helper": "",
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Namespace_Neutron_router"
    }

    router_type_2 = {
        "slot_need": 10,
        "description": "Neutron router implemented in Cisco CSR1kv device",
        "template_id": "00000000-0000-0000-0000-000000000002",
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "ha_enabled_by_default": False,
        "driver": "noop_routertype_driver.NoopL3RouterDriver",
        "cfg_agent_driver": "csr1kv_routing_driver.CSR1kvRoutingDriver",
        "scheduler": "L3RouterHostingDeviceLongestRunningScheduler",
        "shared": True,
        "cfg_agent_service_helper": "routing_svc_helper.RoutingServiceHelper",
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "CSR1kv_router"
    }

    router_type_3 = {
        "slot_need": 10,
        "description": "Neutron router implemented in Cisco CSR1kv device",
        "template_id": "00000000-0000-0000-0000-000000000002",
        "tenant_id": "0b29e1ce8a1440a39b94859bf8d2516c",
        "ha_enabled_by_default": False,
        "driver": "noop_routertype_driver.NoopL3RouterDriver",
        "cfg_agent_driver": "csr1kv_routing_driver.CSR1kvRoutingDriver",
        "scheduler": "L3RouterHostingDeviceLongestRunningScheduler",
        "shared": True,
        "cfg_agent_service_helper": "routing_svc_helper.RoutingServiceHelper",
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "CSR1kv_router"
    }

    TEST.router_types.add(api.RouterType(router_type_1))
    TEST.router_types.add(api.RouterType(router_type_2))
    TEST.router_types.add(api.RouterType(router_type_3))
