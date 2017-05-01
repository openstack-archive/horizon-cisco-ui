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

import dateutil.parser
import json
import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon_cisco_ui.cisco.dfa import dfa_client
from horizon_cisco_ui.cisco.dfa import tables

LOG = logging.getLogger(__name__)


class FabricSummaryTab(tabs.TableTab):
    name = _("Fabric Summary")
    slug = "fabric_summary_tab"
    table_classes = (tables.FabricSummaryTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_fabricsummary_data(self):
        summary = []
        try:
            summary = dfa_client.get_fabric_summary()
        except Exception as exc:
            exceptions.handle(self.request, exc.message)
        return summary


class CFGProfileTab(tabs.TableTab):
    name = _("Network Profiles")
    slug = "cfgprofile_tab"
    table_classes = (tables.CFGProfileTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_cfgprofile_data(self):
        try:
            cfgplist = dfa_client.get_config_profiles_detail()
            profile_list = [p for p in cfgplist
                            if (p.get('profileSubType') ==
                                'network:universal')]
        except Exception as exc:
            profile_list = []
            exceptions.handle(self.request, exc.message)
        return profile_list


class NFEInfoTab(tabs.TableTab):

    name = _("Fabric View")
    slug = "nfe_info_tab"
    table_classes = (tables.ProjectTable, tables.NetworkTable,
                     tables.InstanceTable, )
    template_name = 'cisco/dfa/enablerinfo_tables.html'

    def get_projecttable_data(self):
        try:
            tenant = dict(tenant_id=self.request.user.project_id)
            project_list = dfa_client.get_project_details(tenant)
        except Exception as exc:
            project_list = []
            exceptions.handle(self.request, exc.message)
        return project_list

    def get_networktable_data(self):
        try:
            tenant = dict(tenant_id=self.request.user.project_id)
            netlist = dfa_client.get_network_by_tenant_id(tenant)
        except Exception as exc:
            netlist = []
            exceptions.handle(self.request, exc.message)
        return netlist

    def get_instancetable_data(self):
        try:
            tenant = dict(tenant_id=self.request.user.project_id)
            instance_list = dfa_client.get_instance_by_tenant_id(tenant)
            if not instance_list:
                return []
            agent_list = dfa_client.get_agents_details()
            port = {}
            for agent in agent_list:
                cfg = json.loads(agent.get('config'))
                topo = cfg.get('topo')
                intf = topo.get(cfg.get('veth_intf'))
                host = agent.get('host')
                if not intf:
                    continue
                port.update({host: dict(veth_intf=cfg.get('uplink'),
                            remote_system_name=intf.get('remote_system_name'),
                            remote_port=intf.get('remote_port'))})
            if port:
                for instance in instance_list:
                    instance.update(port.get(instance.get('host')))
        except Exception as exc:
            instance_list = []
            exceptions.handle(self.request, exc.message)
        return instance_list


class NFEAgentTab(tabs.TableTab):
    name = _("Topology View")
    slug = "nfe_agents_tab"
    table_classes = (tables.AgentsTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_agentstable_data(self):
        try:
            agent_list = dfa_client.get_agents_details()
            for agent in agent_list:
                agent["heartbeat"] = dateutil.parser.parse(
                    agent.get('heartbeat'))
                agent["created"] = dateutil.parser.parse(agent.get('created'))
        except Exception as exc:
            agent_list = []
            exceptions.handle(self.request, exc.message)
        return agent_list


class DFATabs(tabs.TabGroup):
    slug = "dfa_tabs"
    tabs = (FabricSummaryTab, CFGProfileTab, NFEInfoTab, NFEAgentTab)
    sticky = True
