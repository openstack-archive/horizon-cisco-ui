# Copyright 2012 Nebula, Inc.
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

from openstack_dashboard.test.test_data import utils


def data(TEST):
    # Test DataContainers for DFA Workflow
    TEST.precreate_network = utils.TestDataContainer()
    TEST.config_profile = utils.TestDataContainer()
    TEST.project = utils.TestDataContainer()
    TEST.network = utils.TestDataContainer()
    TEST.instance = utils.TestDataContainer()
    TEST.agent = utils.TestDataContainer()
    TEST.summary = utils.TestDataContainer()

    precreate_dict = {'tenant_id': '1',
                      'nwk_name': 'net1',
                      'subnet': '10.0.0.0/24',
                      'cfgp': 'defaultNetworkL2Profile'}
    TEST.precreate_network.add(precreate_dict)

    cfg_profile_dict = {'profileSubType': 'network:universal',
                        'description': 'native dhcp EF Profile',
                        'editable': 'yes',
                        'configCommands': 'vlan $vlanId',
                        'profileType': 'IPBD',
                        'profileName': 'nativeDhcpEfProfile',
                        'forwardingMode': 'proxy-gateway',
                        'modifyTimestamp': 'Wed Mar 30 212631 PDT 2016'}
    TEST.config_profile.add(cfg_profile_dict)
    '''
    cfg_profile_dict = {'profileSubType': 'network:universal',
                        'description': 'native dhcp TF Profile',
                        'profileType': 'FPVLAN',
                        'profileName': 'nativeDhcpTfProfile',
                        'forwardingMode': 'anycast-gateway'}
    TEST.config_profile.add(cfg_profile_dict)
   '''
    project_dict = {'project_id': 'cc073fa35b544e27b6a7802e9919afb1',
                    'dci_id': 12344,
                    'project_name': 'Cisco',
                    'result': 'SUCCESS'}
    TEST.project.add(project_dict)

    network_dict = {'network_id': '05df940e-7a68-4ead-9618-ae199c4dc289',
                    'reason': 'Request to DCNM failed: [500] Segment ID: \
                              76388 already exists.',
                    'seg_id': 76388,
                    'result': 'CREATE_FAIL',
                    'config_profile': 'defaultNetworkL2Profile',
                    'network_name': 'net2',
                    'vlan_id': None}
    TEST.network.add(network_dict)

    network_dict = {'network_id': '7c67bc14-8b7b-44ea-9ed5-c3fb36d7bfd9',
                    'reason': None,
                    'seg_id': 76377,
                    'result': 'SUCCESS',
                    'config_profile': 'defaultNetworkUniversalEfProfile',
                    'network_name': 'network1',
                    'vlan_id': 10}
    TEST.network.add(network_dict)

    instance_dict = {'local_vlan': 10,
                     'name': 'INS1',
                     'network_id': '7c67bc14-8b7b-44ea-9ed5-c3fb36d7bfd9',
                     'instance_id': 'e7cd03bed37b4de48f19fc5232056025',
                     'host': 'ctayal-openstack',
                     'veth_intf': 'eth1',
                     'remote_system_name': 'N6k-75',
                     'remote_port': 'Ethernet1/47',
                     'seg_id': 76377,
                     'result': 'SUCCESS',
                     'vdp_vlan': 110,
                     'port_id': '6672d670-9ba9-4889-8754-367bd51165fd'}
    TEST.instance.add(instance_dict)

    agent_dict = {'heartbeat': '2016-09-01T04:40:17.000000',
                  'host': 'compute0',
                  'config': '{"memb_ports": null, "veth_intf": "", \
                              "uplink": ""}',
                  'created': u'2016-07-27T06:34:48.000000'}
    TEST.agent.add(agent_dict)

    summary_dict = {'Fabric Enbaler Version': '2',
                    'DCNM Version': '10.0(1)',
                    'DCNM IP': '172.28.11.151',
                    'Switch Type': 'n6k',
                    'Fabric Type': 'fabricpath',
                    'Fabric ID': '2',
                    'Segment ID Range': '76345-76545'}
    TEST.summary.add(summary_dict)
