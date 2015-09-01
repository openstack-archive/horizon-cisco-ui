# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

from django.core.urlresolvers import reverse
from django import http
from django.utils.http import urlencode
from mox3.mox import IgnoreArg  # noqa
from mox3.mox import IsA  # noqa

from horizon.workflows import views
from openstack_dashboard import api
from openstack_dashboard.api import cinder
from openstack_dashboard.dashboards.project.instances import workflows
from openstack_dashboard.test import helpers
from openstack_dashboard.usage import quotas

from horizon_cisco_ui.dashboards.project.instances.workflows \
    import create_instance as cisco_n1kv_create_instance
from openstack_dashboard.dashboards.project.instances.workflows import \
    create_instance as upstream_create_instance

upstream_create_instance.LaunchInstance.handle = \
    cisco_n1kv_create_instance.N1KvLaunchInstance.handle

upstream_create_instance.LaunchInstance.default_steps = \
    cisco_n1kv_create_instance.N1KvLaunchInstance.default_steps

INDEX_URL = reverse('horizon:project:instances:index')
SEC_GROUP_ROLE_PREFIX = \
    workflows.update_instance.INSTANCE_SEC_GROUP_SLUG + "_role_"
AVAILABLE = api.cinder.VOLUME_STATE_AVAILABLE
VOLUME_SEARCH_OPTS = dict(status=AVAILABLE, bootable=1)
SNAPSHOT_SEARCH_OPTS = dict(status=AVAILABLE)


class CiscoInstanceTests(helpers.TestCase):
    @helpers.create_stubs({api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_snapshot_list',
                                    'volume_list',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.glance: ('image_list_detailed',)})
    def test_launch_instance_get(self,
                                 expect_password_fields=True,
                                 block_device_mapping_v2=True,
                                 custom_flavor_sort=None,
                                 only_one_network=False,
                                 disk_config=True,
                                 config_drive=True,
                                 test_with_profiles=False):
        image = self.images.first()
        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(block_device_mapping_v2)
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        if only_one_network:
            api.neutron.network_list(IsA(http.HttpRequest),
                                     shared=True).AndReturn([])
        else:
            api.neutron.network_list(IsA(http.HttpRequest),
                                     shared=True) \
                .AndReturn(self.networks.list()[1:])
        if test_with_profiles:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(disk_config)
        api.nova.extension_supported(
            'ConfigDrive', IsA(http.HttpRequest)).AndReturn(config_drive)
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest))\
            .AndReturn(self.limits['absolute'])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())

        self.mox.ReplayAll()

        url = reverse('horizon:project:instances:launch')
        params = urlencode({"source_type": "image_id",
                            "source_id": image.id})
        res = self.client.get("%s?%s" % (url, params))

        workflow = res.context['workflow']
        self.assertTemplateUsed(res, views.WorkflowView.template_name)
        self.assertEqual(res.context['workflow'].name,
                         workflows.LaunchInstance.name)
        step = workflow.get_step("setinstancedetailsaction")
        self.assertEqual(step.action.initial['image_id'], image.id)
        self.assertQuerysetEqual(
            workflow.steps,
            ['<SetInstanceDetails: setinstancedetailsaction>',
             '<SetAccessControls: setaccesscontrolsaction>',
             '<N1KvSetNetwork: n1kvsetnetworkaction>',
             '<PostCreationStep: customizeaction>',
             '<SetAdvanced: setadvancedaction>'])

        if custom_flavor_sort == 'id':
            # Reverse sorted by id
            sorted_flavors = (
                ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'm1.metadata'),
                ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'm1.secret'),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'm1.massive'),
                ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'm1.tiny'),
            )
        elif custom_flavor_sort == 'name':
            sorted_flavors = (
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'm1.massive'),
                ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'm1.metadata'),
                ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'm1.secret'),
                ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'm1.tiny'),
            )
        elif custom_flavor_sort == helpers.my_custom_sort:
            sorted_flavors = (
                ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'm1.secret'),
                ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'm1.tiny'),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'm1.massive'),
                ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'm1.metadata'),
            )
        else:
            # Default - sorted by RAM
            sorted_flavors = (
                ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'm1.tiny'),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'm1.massive'),
                ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'm1.secret'),
                ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'm1.metadata'),
            )

        select_options = '\n'.join([
            '<option value="%s">%s</option>' % (f[0], f[1])
            for f in sorted_flavors
        ])
        self.assertContains(res, select_options)

        password_field_label = 'Admin Pass'
        if expect_password_fields:
            self.assertContains(res, password_field_label)
        else:
            self.assertNotContains(res, password_field_label)

        boot_from_image_field_label = 'Boot from image (creates a new volume)'
        if block_device_mapping_v2:
            self.assertContains(res, boot_from_image_field_label)
        else:
            self.assertNotContains(res, boot_from_image_field_label)

        checked_label = '<label for="id_network_0"><input checked="checked"'
        if only_one_network:
            self.assertContains(res, checked_label)
        else:
            self.assertNotContains(res, checked_label)

        disk_config_field_label = 'Disk Partition'
        if disk_config:
            self.assertContains(res, disk_config_field_label)
        else:
            self.assertNotContains(res, disk_config_field_label)

        config_drive_field_label = 'Configuration Drive'
        if config_drive:
            self.assertContains(res, config_drive_field_label)
        else:
            self.assertNotContains(res, config_drive_field_label)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_get_with_profile(self):
        self.test_launch_instance_get(test_with_profiles=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    @helpers.create_stubs({api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_snapshot_list',
                                    'volume_list',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.glance: ('image_list_detailed',)})
    def test_launch_instance_get_bootable_volumes(self,
                                                  block_device_mapping_v2=True,
                                                  only_one_network=False,
                                                  disk_config=True,
                                                  config_drive=True):
        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(block_device_mapping_v2)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        if only_one_network:
            api.neutron.network_list(IsA(http.HttpRequest),
                                     shared=True).AndReturn([])
        else:
            api.neutron.network_list(IsA(http.HttpRequest),
                                     shared=True) \
                .AndReturn(self.networks.list()[1:])

        policy_profiles = self.policy_profiles.list()
        api.neutron.profile_list(IsA(http.HttpRequest),
                                 'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(disk_config)
        api.nova.extension_supported(
            'ConfigDrive', IsA(http.HttpRequest)).AndReturn(config_drive)
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest))\
            .AndReturn(self.limits['absolute'])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())

        self.mox.ReplayAll()

        url = reverse('horizon:project:instances:launch')
        res = self.client.get(url)

        bootable_volumes = [v.id for v in self.volumes.list()
                            if (v.bootable == 'true' and
                                v.status == 'available')]

        volume_sources = (res.context_data['workflow'].steps[0].
                          action.fields['volume_id'].choices)

        volume_sources_ids = []
        for volume in volume_sources:
            self.assertTrue(volume[0].split(":vol")[0] in bootable_volumes or
                            volume[0] == '')
            if volume[0] != '':
                volume_sources_ids.append(volume[0].split(":vol")[0])

        for volume in bootable_volumes:
            self.assertTrue(volume in volume_sources_ids)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'server_create',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post(self,
                                  disk_config=True,
                                  config_drive=True,
                                  test_with_profile=False,
                                  test_with_multi_nics=False):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        nics = [{"net-id": self.networks.first().id, "v4-fixed-ip": ''}]
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            policy_profile_id = self.policy_profiles.first().id
            port_one = self.ports.first()
            nics = [{"port-id": port_one.id}]
            api.neutron.profile_list(
                IsA(http.HttpRequest),
                'policy').AndReturn(policy_profiles)
            api.neutron.port_create(IsA(http.HttpRequest),
                                    self.networks.first().id,
                                    policy_profile_id=policy_profile_id)\
                .AndReturn(port_one)
            if test_with_multi_nics:
                port_two = self.ports.get(name="port5")
                nics = [{"port-id": port_one.id},
                        {"port-id": port_two.id}]
                # Add a second port to test multiple nics
                api.neutron.port_create(IsA(http.HttpRequest),
                                        self.networks.get(name="net4")['id'],
                                        policy_profile_id=policy_profile_id).\
                    AndReturn(port_two)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(disk_config)
        api.nova.extension_supported(
            'ConfigDrive', IsA(http.HttpRequest)).AndReturn(config_drive)
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        if disk_config:
            disk_config_value = u'AUTO'
        else:
            disk_config_value = None
        if config_drive:
            config_drive_value = True
        else:
            config_drive_value = None
        api.nova.server_create(IsA(http.HttpRequest),
                               server.name,
                               image.id,
                               flavor.id,
                               keypair.name,
                               customization_script,
                               [sec_group.name],
                               block_device_mapping=None,
                               block_device_mapping_v2=None,
                               nics=nics,
                               availability_zone=avail_zone.zoneName,
                               instance_count=IsA(int),
                               admin_pass=u'',
                               disk_config=disk_config_value,
                               config_drive=config_drive_value)
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()
        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': image.id,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'availability_zone': avail_zone.zoneName,
                     'volume_type': '',
                     'network': self.networks.first().id,
                     'count': 1}
        if disk_config:
            form_data['disk_config'] = 'AUTO'
        if config_drive:
            form_data['config_drive'] = True
        if test_with_profile:
            form_data['profile'] = self.policy_profiles.first().id
            if test_with_multi_nics:
                form_data['network'] = [self.networks.first().id,
                                        self.networks.get(name="net4")['id']]
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_post_with_profile(self):
        self.test_launch_instance_post(test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_post_with_profile_and_multi_nics(self):
        self.test_launch_instance_post(test_with_profile=True,
                                       test_with_multi_nics=True)

    def _test_launch_instance_post_with_profile_and_port_error(
        self,
        test_with_multi_nics=False,
    ):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
                .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
                .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
                .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
                .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(IsA(http.HttpRequest),
                                       filters={'is_public': True,
                                                'status': 'active'}) \
                  .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])

        policy_profiles = self.policy_profiles.list()
        policy_profile_id = self.policy_profiles.first().id
        port_one = self.ports.first()
        api.neutron.profile_list(
            IsA(http.HttpRequest),
            'policy').AndReturn(policy_profiles)
        if test_with_multi_nics:
            api.neutron.port_create(IsA(http.HttpRequest),
                                    self.networks.first().id,
                                    policy_profile_id=policy_profile_id) \
               .AndReturn(port_one)
            # Add a second port which has the exception to test multiple nics
            api.neutron.port_create(IsA(http.HttpRequest),
                                    self.networks.get(name="net4")['id'],
                                    policy_profile_id=policy_profile_id) \
               .AndRaise(self.exceptions.neutron)
            # Delete the first port
            api.neutron.port_delete(IsA(http.HttpRequest),
                                    port_one.id)
        else:
            api.neutron.port_create(IsA(http.HttpRequest),
                                    self.networks.first().id,
                                    policy_profile_id=policy_profile_id) \
               .AndRaise(self.exceptions.neutron)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
                .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
              .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
              .AndReturn([])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
              .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': image.id,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'availability_zone': avail_zone.zoneName,
                     'volume_type': '',
                     'network': self.networks.first().id,
                     'count': 1,
                     'disk_config': 'AUTO',
                     'config_drive': True,
                     'profile': self.policy_profiles.first().id}
        if test_with_multi_nics:
            form_data['network'] = [self.networks.first().id,
                                    self.networks.get(name="net4")['id']]
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',
                                         'port_delete',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post_with_profile_and_port_error(self):
        self._test_launch_instance_post_with_profile_and_port_error()

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',
                                         'port_delete',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_lnch_inst_post_w_profile_and_multi_nics_w_port_error(self):
        self._test_launch_instance_post_with_profile_and_port_error(
            test_with_multi_nics=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'server_create',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post_boot_from_volume(
        self,
        test_with_profile=False,
        test_with_bdmv2=False
    ):
        flavor = self.flavors.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        volume = self.volumes.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        volume_choice = "%s:vol" % volume.id
        if test_with_bdmv2:
            volume_source_id = volume.id.split(':')[0]
            block_device_mapping = None
            block_device_mapping_2 = [
                {'device_name': u'vda',
                 'source_type': 'volume',
                 'destination_type': 'volume',
                 'delete_on_termination': 0,
                 'uuid': volume_source_id,
                 'boot_index': '0',
                 'volume_size': 1
                 }
            ]
        else:
            block_device_mapping = {device_name: u"%s::0" % volume_choice}
            block_device_mapping_2 = None

        nics = [{"net-id": self.networks.first().id, "v4-fixed-ip": ''}]
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(test_with_bdmv2)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            policy_profile_id = self.policy_profiles.first().id
            port = self.ports.first()
            api.neutron.profile_list(
                IsA(http.HttpRequest),
                'policy').AndReturn(policy_profiles)
            api.neutron.port_create(
                IsA(http.HttpRequest),
                self.networks.first().id,
                policy_profile_id=policy_profile_id).AndReturn(port)
            nics = [{"port-id": port.id}]
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(test_with_bdmv2)

        api.nova.server_create(IsA(http.HttpRequest),
                               server.name,
                               '',
                               flavor.id,
                               keypair.name,
                               customization_script,
                               [sec_group.name],
                               block_device_mapping=block_device_mapping,
                               block_device_mapping_v2=block_device_mapping_2,
                               nics=nics,
                               availability_zone=avail_zone.zoneName,
                               instance_count=IsA(int),
                               admin_pass=u'',
                               disk_config=u'AUTO',
                               config_drive=True)
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'volume_id',
                     'source_id': volume_choice,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'availability_zone': avail_zone.zoneName,
                     'volume_size': '1',
                     'volume_id': volume_choice,
                     'device_name': device_name,
                     'network': self.networks.first().id,
                     'count': 1,
                     'disk_config': 'AUTO',
                     'config_drive': True}
        if test_with_profile:
            form_data['profile'] = self.policy_profiles.first().id
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_post_boot_from_volume_with_profile(self):
        self.test_launch_instance_post_boot_from_volume(test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_post_boot_from_volume_with_profile_with_bdmv2(
            self):
        self.test_launch_instance_post_boot_from_volume(
            test_with_profile=True,
            test_with_bdmv2=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create'),
                           api.nova: ('server_create',
                                      'extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'tenant_absolute_limits',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post_no_images_available_boot_from_volume(
        self,
        test_with_profile=False,
    ):
        flavor = self.flavors.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        volume = self.volumes.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        volume_choice = "%s:vol" % volume.id
        block_device_mapping = {device_name: u"%s::0" % volume_choice}
        nics = [{"net-id": self.networks.first().id, "v4-fixed-ip": ''}]
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            policy_profile_id = self.policy_profiles.first().id
            port = self.ports.first()
            api.neutron.profile_list(
                IsA(http.HttpRequest),
                'policy').AndReturn(policy_profiles)
            api.neutron.port_create(
                IsA(http.HttpRequest),
                self.networks.first().id,
                policy_profile_id=policy_profile_id).AndReturn(port)
            nics = [{"port-id": port.id}]
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(False)
        api.nova.server_create(IsA(http.HttpRequest),
                               server.name,
                               '',
                               flavor.id,
                               keypair.name,
                               customization_script,
                               [sec_group.name],
                               block_device_mapping=block_device_mapping,
                               block_device_mapping_v2=None,
                               nics=nics,
                               availability_zone=avail_zone.zoneName,
                               instance_count=IsA(int),
                               admin_pass=u'',
                               disk_config='MANUAL',
                               config_drive=True)

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'volume_id',
                     # 'image_id': '',
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'availability_zone': avail_zone.zoneName,
                     'network': self.networks.first().id,
                     'volume_type': 'volume_id',
                     'volume_id': volume_choice,
                     'device_name': device_name,
                     'count': 1,
                     'disk_config': 'MANUAL',
                     'config_drive': True}
        if test_with_profile:
            form_data['profile'] = self.policy_profiles.first().id
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_lnch_inst_post_no_images_avail_boot_from_vol_with_profile(self):
        self.test_launch_instance_post_no_images_available_boot_from_volume(
            test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'tenant_absolute_limits',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post_no_images_available(self,
                                                      test_with_profile=False):
        flavor = self.flavors.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
           .AndReturn(self.limits['absolute'])
        api.glance.image_list_detailed(IsA(http.HttpRequest),
                                       filters={'is_public': True,
                                                'status': 'active'}) \
            .AndReturn([[], False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': '',
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'availability_zone': avail_zone.zoneName,
                     'volume_type': '',
                     'count': 1}
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertFormErrors(res, 1, "You must select an image.")
        self.assertTemplateUsed(res, views.WorkflowView.template_name)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_instance_post_no_images_available_with_profile(self):
        self.test_launch_instance_post_no_images_available(
            test_with_profile=True)

    @helpers.create_stubs({
        api.glance: ('image_list_detailed',),
        api.neutron: ('network_list',
                      'profile_list',
                      'port_create',),
        api.nova: ('extension_supported',
                   'flavor_list',
                   'keypair_list',
                   'availability_zone_list',
                   'server_create',),
        api.network: ('security_group_list',),
        cinder: ('volume_list',
                 'volume_snapshot_list',),
        quotas: ('tenant_quota_usages',)})
    def test_launch_instance_post_boot_from_snapshot(
        self,
        test_with_profile=False,
    ):
        flavor = self.flavors.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        avail_zone = self.availability_zones.first()
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.glance.image_list_detailed(IsA(http.HttpRequest),
                                       filters={'is_public': True,
                                                'status': 'active'}) \
            .AndReturn([[], False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)

        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])

        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)

        self.mox.ReplayAll()

        bad_snapshot_id = 'a-bogus-id'

        form_data = {'flavor': flavor.id,
                     'source_type': 'instance_snapshot_id',
                     'instance_snapshot_id': bad_snapshot_id,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'availability_zone': avail_zone.zoneName,
                     'network': self.networks.first().id,
                     'volume_id': '',
                     'volume_snapshot_id': '',
                     'image_id': '',
                     'device_name': 'vda',
                     'count': 1,
                     'profile': '',
                     'customization_script': ''}

        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertFormErrors(res, 1, "You must select a snapshot.")

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           api.network: ('security_group_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',)})
    def test_launch_flavorlist_error(self,
                                     test_with_profile=False):
        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
            .AndReturn(self.limits['absolute'])
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndRaise(self.exceptions.nova)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndRaise(self.exceptions.nova)
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())

        self.mox.ReplayAll()

        url = reverse('horizon:project:instances:launch')
        res = self.client.get(url)

        self.assertTemplateUsed(res, views.WorkflowView.template_name)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_flavorlist_error_with_profile(self):
        self.test_launch_flavorlist_error(test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'server_create',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_form_keystone_exception(self,
                                            test_with_profile=False):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        nics = [{"net-id": self.networks.first().id, "v4-fixed-ip": ''}]
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE)]
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn(volumes)
        api.nova.flavor_list(IgnoreArg()).AndReturn(self.flavors.list())
        api.nova.keypair_list(IgnoreArg()).AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            policy_profile_id = self.policy_profiles.first().id
            port = self.ports.first()
            api.neutron.profile_list(
                IsA(http.HttpRequest),
                'policy').AndReturn(policy_profiles)
            api.neutron.port_create(
                IsA(http.HttpRequest),
                self.networks.first().id,
                policy_profile_id=policy_profile_id).AndReturn(port)
            nics = [{"port-id": port.id}]
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        api.nova.server_create(IsA(http.HttpRequest),
                               server.name,
                               image.id,
                               flavor.id,
                               keypair.name,
                               customization_script,
                               [sec_group.name],
                               block_device_mapping=None,
                               block_device_mapping_v2=None,
                               nics=nics,
                               availability_zone=avail_zone.zoneName,
                               instance_count=IsA(int),
                               admin_pass='password',
                               disk_config='AUTO',
                               config_drive=False) \
            .AndRaise(self.exceptions.keystone)
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'source_id': image.id,
                     'volume_size': '1',
                     'image_id': image.id,
                     'availability_zone': avail_zone.zoneName,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'volume_type': '',
                     'network': self.networks.first().id,
                     'count': 1,
                     'admin_pass': 'password',
                     'confirm_admin_pass': 'password',
                     'disk_config': 'AUTO',
                     'config_drive': False}
        if test_with_profile:
            form_data['profile'] = self.policy_profiles.first().id
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_keystone_exception_with_profile(self):
        self.test_launch_form_keystone_exception(test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_launch_form_instance_count_error(self,
                                              test_with_profile=False):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        volume = self.volumes.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        volume_choice = "%s:vol" % volume.id
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])

        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
           .AndReturn(self.limits['absolute'])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': image.id,
                     'availability_zone': avail_zone.zoneName,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'volume_type': 'volume_id',
                     'volume_id': volume_choice,
                     'device_name': device_name,
                     'count': 0}
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertContains(res, "greater than or equal to 1")

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_instance_count_error_with_profile(self):
        self.test_launch_form_instance_count_error(test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def _test_launch_form_count_error(self, resource,
                                      avail, test_with_profile=False):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        volume = self.volumes.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        volume_choice = "%s:vol" % volume.id
        quota_usages = self.quota_usages.first()
        if resource == 'both':
            quota_usages['cores']['available'] = avail
            quota_usages['ram']['available'] = 512
        else:
            quota_usages[resource]['available'] = avail

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])

        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
           .AndReturn(self.limits['absolute'])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': image.id,
                     'availability_zone': avail_zone.zoneName,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'volume_type': 'volume_id',
                     'volume_id': volume_choice,
                     'device_name': device_name,
                     'count': 2}
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        if resource == 'ram':
            msg = ("The following requested resource(s) exceed quota(s): "
                   "RAM(Available: %s" % avail)
        if resource == 'cores':
            msg = ("The following requested resource(s) exceed quota(s): "
                   "Cores(Available: %s" % avail)
        if resource == 'both':
            msg = ("The following requested resource(s) exceed quota(s): "
                   "Cores(Available: %(avail)s, Requested: 2), RAM(Available: "
                   "512, Requested: 1024)" % {'avail': avail})
        self.assertContains(res, msg)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_cores_count_error(self):
        self._test_launch_form_count_error('cores', 1, test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_ram_count_error(self):
        self._test_launch_form_count_error('ram', 512, test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_ram_cores_count_error(self):
        self._test_launch_form_count_error('both', 1, test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def _test_launch_form_instance_requirement_error(self, image, flavor,
                                                     test_with_profile=False):
        keypair = self.keypairs.first()
        server = self.servers.first()
        volume = self.volumes.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        volume_choice = "%s:vol" % volume.id
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])

        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
           .AndReturn(self.limits['absolute'])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'image_id': image.id,
                     'availability_zone': avail_zone.zoneName,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'volume_type': 'volume_id',
                     'volume_id': volume_choice,
                     'device_name': device_name,
                     'count': 1}

        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)
        msg = "The flavor &#39;%s&#39; is too small" % flavor.name
        self.assertContains(res, msg)

    def test_launch_form_instance_requirement_error_disk(
        self,
        test_with_profile=False,
    ):
        flavor = self.flavors.first()
        image = self.images.first()
        image.min_ram = flavor.ram
        image.min_disk = flavor.disk + 1
        self._test_launch_form_instance_requirement_error(image, flavor,
                                                          test_with_profile)

    def test_launch_form_instance_requirement_error_ram(
        self,
        test_with_profile=False,
    ):
        flavor = self.flavors.first()
        image = self.images.first()
        image.min_ram = flavor.ram + 1
        image.min_disk = flavor.disk
        self._test_launch_form_instance_requirement_error(image, flavor,
                                                          test_with_profile)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_instance_requirement_error_disk_with_profile(self):
        self.test_launch_form_instance_requirement_error_disk(
            test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_instance_requirement_error_ram_with_profile(self):
        self.test_launch_form_instance_requirement_error_ram(
            test_with_profile=True)

    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'tenant_absolute_limits',
                                      'availability_zone_list',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def _test_launch_form_instance_volume_size(self, image, volume_size, msg,
                                               test_with_profile=False,
                                               volumes=None):
        flavor = self.flavors.get(name='m1.massive')
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        device_name = u'vda'
        quota_usages = self.quota_usages.first()
        quota_usages['cores']['available'] = 2000
        if volumes is not None:
            quota_usages['volumes']['available'] = volumes
        else:
            api.nova.flavor_list(IsA(http.HttpRequest)) \
                .AndReturn(self.flavors.list())

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        volumes = [v for v in self.volumes.list()
                   if (v.status == AVAILABLE and v.bootable == 'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])

        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
            .AndReturn(self.limits['absolute'])
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {
            'flavor': flavor.id,
            'source_type': 'volume_image_id',
            'image_id': image.id,
            'availability_zone': avail_zone.zoneName,
            'keypair': keypair.name,
            'name': server.name,
            'script_source': 'raw',
            'script_data': customization_script,
            'project_id': self.tenants.first().id,
            'user_id': self.user.id,
            'groups': sec_group.name,
            'volume_size': volume_size,
            'device_name': device_name,
            'count': 1
        }
        url = reverse('horizon:project:instances:launch')

        res = self.client.post(url, form_data)
        self.assertContains(res, msg)

    def test_launch_form_instance_volume_size_error(self,
                                                    test_with_profile=False):
        image = self.images.get(name='protected_images')
        volume_size = image.min_disk / 2
        msg = ("The Volume size is too small for the &#39;%s&#39; image" %
               image.name)
        self._test_launch_form_instance_volume_size(image, volume_size, msg,
                                                    test_with_profile)

    def test_launch_form_instance_non_int_volume_size(self,
                                                      test_with_profile=False):
        image = self.images.get(name='protected_images')
        msg = "Enter a whole number."
        self._test_launch_form_instance_volume_size(image, 1.5, msg,
                                                    test_with_profile)

    def test_launch_form_instance_volume_exceed_quota(self):
        image = self.images.get(name='protected_images')
        msg = "Requested volume exceeds quota: Available: 0, Requested: 1"
        self._test_launch_form_instance_volume_size(image, image.min_disk,
                                                    msg, False, 0)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_instance_volume_size_error_with_profile(self):
        self.test_launch_form_instance_volume_size_error(
            test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_launch_form_instance_non_int_volume_size_with_profile(self):
        self.test_launch_form_instance_non_int_volume_size(
            test_with_profile=True)

    @helpers.create_stubs({api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'tenant_absolute_limits',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_snapshot_list',
                                    'volume_list',),
                           api.neutron: ('network_list',
                                         'profile_list'),
                           api.glance: ('image_list_detailed',)})
    def test_select_default_keypair_if_only_one(self,
                                                test_with_profile=False):
        keypair = self.keypairs.first()

        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn([])
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn([])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        if test_with_profile:
            policy_profiles = self.policy_profiles.list()
            api.neutron.profile_list(IsA(http.HttpRequest),
                                     'policy').AndReturn(policy_profiles)
        api.nova.tenant_absolute_limits(IsA(http.HttpRequest)) \
           .AndReturn(self.limits['absolute'])
        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())
        api.nova.keypair_list(IsA(http.HttpRequest)) \
            .AndReturn([keypair])
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())

        self.mox.ReplayAll()

        url = reverse('horizon:project:instances:launch')
        res = self.client.get(url)
        self.assertContains(
            res, "<option selected='selected' value='%(key)s'>"
                 "%(key)s</option>" % {'key': keypair.name},
            html=True,
            msg_prefix="The default key pair was not selected.")

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    def test_select_default_keypair_if_only_one_with_profile(self):
        self.test_select_default_keypair_if_only_one(test_with_profile=True)

    @helpers.update_settings(
        OPENSTACK_NEUTRON_NETWORK={'profile_support': 'cisco'})
    @helpers.create_stubs({api.glance: ('image_list_detailed',),
                           api.neutron: ('network_list',
                                         'profile_list',
                                         'port_create',
                                         'port_delete'),
                           api.nova: ('extension_supported',
                                      'flavor_list',
                                      'keypair_list',
                                      'availability_zone_list',
                                      'server_create',),
                           api.network: ('security_group_list',),
                           cinder: ('volume_list',
                                    'volume_snapshot_list',),
                           quotas: ('tenant_quota_usages',)})
    def test_port_cleanup_called_on_failed_vm_launch(self):
        flavor = self.flavors.first()
        image = self.images.first()
        keypair = self.keypairs.first()
        server = self.servers.first()
        sec_group = self.security_groups.first()
        avail_zone = self.availability_zones.first()
        customization_script = 'user data'
        quota_usages = self.quota_usages.first()

        api.nova.extension_supported('BlockDeviceMappingV2Boot',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        volumes = [v for v in self.volumes.list() if (v.status == AVAILABLE
                                                      and v.bootable ==
                                                      'true')]
        cinder.volume_list(IsA(http.HttpRequest),
                           search_opts=VOLUME_SEARCH_OPTS) \
            .AndReturn(volumes)
        volumes = [v for v in self.volumes.list() if (v.status == AVAILABLE)]
        cinder.volume_snapshot_list(IsA(http.HttpRequest),
                                    search_opts=SNAPSHOT_SEARCH_OPTS) \
            .AndReturn(volumes)
        api.nova.flavor_list(IgnoreArg()).AndReturn(self.flavors.list())
        api.nova.keypair_list(IgnoreArg()).AndReturn(self.keypairs.list())
        api.network.security_group_list(IsA(http.HttpRequest)) \
            .AndReturn(self.security_groups.list())
        api.nova.availability_zone_list(IsA(http.HttpRequest)) \
            .AndReturn(self.availability_zones.list())
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'is_public': True, 'status': 'active'}) \
            .AndReturn([self.images.list(), False, False])
        api.glance.image_list_detailed(
            IsA(http.HttpRequest),
            filters={'property-owner_id': self.tenant.id,
                     'status': 'active'}) \
            .AndReturn([[], False, False])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 tenant_id=self.tenant.id,
                                 shared=False) \
            .AndReturn(self.networks.list()[:1])
        api.neutron.network_list(IsA(http.HttpRequest),
                                 shared=True) \
            .AndReturn(self.networks.list()[1:])
        policy_profiles = self.policy_profiles.list()
        policy_profile_id = self.policy_profiles.first().id
        port = self.ports.first()
        api.neutron.profile_list(
            IsA(http.HttpRequest), 'policy').AndReturn(policy_profiles)
        api.neutron.port_create(
            IsA(http.HttpRequest),
            self.networks.first().id,
            policy_profile_id=policy_profile_id).AndReturn(port)
        nics = [{"port-id": port.id}]
        api.nova.extension_supported('DiskConfig',
                                     IsA(http.HttpRequest)) \
            .AndReturn(True)
        api.nova.extension_supported('ConfigDrive',
                                     IsA(http.HttpRequest)).AndReturn(True)
        api.nova.server_create(IsA(http.HttpRequest),
                               server.name,
                               image.id,
                               flavor.id,
                               keypair.name,
                               customization_script,
                               [sec_group.name],
                               block_device_mapping=None,
                               block_device_mapping_v2=None,
                               nics=nics,
                               availability_zone=avail_zone.zoneName,
                               instance_count=IsA(int),
                               admin_pass='password',
                               disk_config='AUTO',
                               config_drive=False) \
            .AndRaise(self.exceptions.neutron)
        api.neutron.port_delete(IsA(http.HttpRequest), port.id)
        quotas.tenant_quota_usages(IsA(http.HttpRequest)) \
            .AndReturn(quota_usages)
        api.nova.flavor_list(IsA(http.HttpRequest)) \
            .AndReturn(self.flavors.list())

        self.mox.ReplayAll()

        form_data = {'flavor': flavor.id,
                     'source_type': 'image_id',
                     'source_id': image.id,
                     'volume_size': '1',
                     'image_id': image.id,
                     'availability_zone': avail_zone.zoneName,
                     'keypair': keypair.name,
                     'name': server.name,
                     'script_source': 'raw',
                     'script_data': customization_script,
                     'project_id': self.tenants.first().id,
                     'user_id': self.user.id,
                     'groups': sec_group.name,
                     'volume_type': '',
                     'network': self.networks.first().id,
                     'count': 1,
                     'admin_pass': 'password',
                     'confirm_admin_pass': 'password',
                     'disk_config': 'AUTO',
                     'config_drive': False,
                     'profile': self.policy_profiles.first().id}
        url = reverse('horizon:project:instances:launch')
        res = self.client.post(url, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)
