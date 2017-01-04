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

from horizon_cisco_ui.cisco.dfa.tabs import dfa_client as dc
from horizon_cisco_ui.cisco.dfa.test import test_data

import mock
from openstack_dashboard.test import helpers as test


class DFATestCase(test.BaseAdminViewTests):

    def setUp(self):
        super(DFATestCase, self).setUp()
        self.dfa_client = dc.DFAClient

    def _setup_test_data(self):
        super(DFATestCase, self)._setup_test_data()
        test_data.data(self)

    def _test_base_index(self):
        profiles = self.dfa_config_profile.list()
        projects = self.dfa_project.list()
        networks = self.dfa_network.list()
        instances = self.dfa_instance.list()
        agents = self.dfa_agent.list()
        summary = self.dfa_summary.list()[0]

        with mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                        '.get_config_profiles_detail', return_value=profiles), \
                mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                           '.get_network_by_tenant_id',
                           return_value=networks), \
                mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                           '.get_instance_by_tenant_id',
                           return_value=instances), \
                mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                           '.get_project_details',
                           return_value=projects), \
                mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                           '.get_fabric_summary',
                           return_value=summary), \
                mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                           '.get_agents_details',
                           return_value=agents):
            res = self.client.get(reverse('horizon:cisco:dfa:index'))

        self.assertTemplateUsed(res, 'cisco/dfa/index.html')

        return res

    def test_fabric_summary_tab_index(self):
        res = self._test_base_index()
        services_tab = res.context['tab_group'].get_tab('fabric_summary_tab')
        self.assertEqual(
            services_tab._tables['fabricsummary'].data,
            [summary for summary in self.dfa_summary.list()[0]])

    def test_cfg_profile_index(self):
        res = self._test_base_index()
        services_tab = res.context['tab_group'].get_tab('cfgprofile_tab')
        self.assertEqual(
            services_tab._tables['cfgprofile'].data,
            [profiles for profiles in self.dfa_config_profile.list()])

    def test_nfe_info_index(self):
        res = self._test_base_index()
        services_tab = res.context['tab_group'].get_tab('nfe_info_tab')
        self.assertEqual(
            services_tab._tables['projecttable'].data,
            [project for project in self.dfa_project.list()])

        self.assertEqual(
            services_tab._tables['networktable'].data,
            [network for network in self.dfa_network.list()])

    def test_nfe_agents_index(self):
        res = self._test_base_index()
        services_tab = res.context['tab_group'].get_tab('nfe_agents_tab')
        self.assertEqual(
            services_tab._tables['agentstable'].data,
            [agent for agent in self.dfa_agent.list()])

    def test_agent_detail(self):
        agent = self.dfa_agent.list()
        with mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                        '.get_agent_details_per_host',
                        return_value=agent):
            res = self.client.get(reverse('horizon:cisco:dfa:detail',
                                          args=['compute0']))
        self.assertTemplateUsed(res, 'cisco/dfa/detail.html')

    def test_agent_detail_exception(self):
        with mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                        '.get_agent_details_per_host',
                        side_effect=dc.exceptions.NotAvailable):
            url = reverse('horizon:cisco:dfa:detail', args=['compute0'])
            res = self.client.get(url)

        redir_url = reverse('horizon:cisco:dfa:index')
        self.assertRedirectsNoFollow(res, redir_url)

    def test_associate_dci_to_project(self):
        formdata = {'project_id': 123456, 'dci_id': 1001}
        with mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                        '.do_associate_dci_id_to_project'):
            url = reverse('horizon:cisco:dfa:associate', args=['123456'])
            res = self.client.post(url, formdata)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, '/cisco/dfa/')

    def test_disassociate_dci_to_project(self):
        formdata = {'project_id': 123456, 'dci_id': 0}
        with mock.patch('horizon_cisco_ui.cisco.dfa.tabs.dfa_client'
                        '.do_associate_dci_id_to_project'):
            url = reverse('horizon:cisco:dfa:disassociate', args=['123456'])
            res = self.client.post(url, formdata)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, '/cisco/dfa/')
