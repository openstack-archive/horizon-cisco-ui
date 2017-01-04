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

from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables

import logging

LOG = logging.getLogger(__name__)


class AssociateDCIAction(tables.LinkAction):
    name = "associate"
    verbose_name = _("Associate DCI ID")
    url = "horizon:cisco:dfa:associate"
    classes = ("ajax-modal",)
    icon = "link"


class DisassociateDCIAction(tables.LinkAction):
    name = "dis_associate"
    verbose_name = _("Disassociate DCI ID")
    url = "horizon:cisco:dfa:disassociate"
    classes = ("ajax-modal",)
    icon = "link"


class SearchFilterAction(tables.FilterAction):
    name = "searchfilter"


def get_result(obj):
    if obj.get('result') == 'SUCCESS':
        return obj.get('result')

    if 'network_id' in obj:
        obj_id = obj.get('network_id')
    elif 'project_id' in obj:
        obj_id = obj.get('project_id')
    elif 'port_id' in obj:
        obj_id = obj.get('port_id')
    else:
        obj_id = 'none'

    if 'reason' in obj:
        template_name = 'cisco/dfa/_reason.html'
        context = {
            "result": obj.get('result'),
            "id": obj_id,
            "reason": obj.get('reason')
        }
        return template.loader.render_to_string(template_name, context)
    return obj.get('result')


def get_instance_detail(obj):
    if 'instance_id' in obj:
        template_name = 'cisco/dfa/_instance.html'
        context = {
            "name": obj.get('name'),
            "nw_name": obj.get('network_name'),
            "id": ''.join(e for e in obj.get('instance_id') if e.isalnum()),
            "mac": obj.get('mac'),
            "ip": obj.get('ip'),
            "port": obj.get('port_id'),
            "host_port": ', '.join((obj.get('host'), obj.get('veth_intf'))),
            "TOR_port": ', '.join((obj.get('remote_system_name'),
                                  obj.get('remote_port')))
        }
        return template.loader.render_to_string(template_name, context)

    return obj.get('name')


class FabricSummaryTable(tables.DataTable):
    key = tables.Column("key", sortable=False,
                        verbose_name=_("Fabric Property"))
    value = tables.Column("value",
                          verbose_name=_("Value"))

    def get_object_id(self, obj):
        return obj.get('key')

    class Meta(object):
        name = "fabricsummary"
        verbose_name = _("Fabric Summary")
        table_actions = (SearchFilterAction, )
        multi_select = False


class CFGProfileTable(tables.DataTable):
    profile_name = tables.Column("profileName", sortable=False,
                                 verbose_name=_("Profile Name"),
                                 link='horizon:cisco:dfa:detailprofile')

    def get_object_id(self, obj):
        return ':'.join((obj.get('profileName'), obj.get('profileType')))

    class Meta(object):
        name = "cfgprofile"
        verbose_name = _("CFGProfile")
        table_actions = (SearchFilterAction, )
        multi_select = False


class ProjectTable(tables.DataTable):
    project_name = tables.Column("project_name",
                                 verbose_name=_("Project Name"))
    project_id = tables.Column("project_id", verbose_name=_("Project ID"))
    seg_id = tables.Column("seg_id", verbose_name=_("L3 VNI"))
    dci_id = tables.Column("dci_id", verbose_name=_("DCI ID"))
    result = tables.Column(get_result, verbose_name=_("Result"))

    def get_object_id(self, obj):
        return obj.get('project_id')

    class Meta(object):
        name = "projecttable"
        hidden_title = False
        verbose_name = _("Projects")
        row_actions = (AssociateDCIAction, DisassociateDCIAction, )


class NetworkTable(tables.DataTable):
    network_name = tables.Column("network_name", verbose_name=_("Name"))
    network_id = tables.Column("network_id", verbose_name=_("ID"))
    config_profile = tables.Column("config_profile",
                                   verbose_name=_("Network Profile"))
    seg_id = tables.Column("seg_id", verbose_name=_("Segmentation ID"))
    vlan_id = tables.Column("vlan_id", verbose_name=_("Vlan ID"))
    result = tables.Column(get_result, verbose_name=_("Result"))

    def get_object_id(self, obj):
        return obj.get('network_id')

    class Meta(object):
        name = "networktable"
        hidden_title = False
        verbose_name = _("Networks")
        table_actions = (SearchFilterAction,)
        multi_select = False


class InstanceTable(tables.DataTable):
    instance_name = tables.Column(get_instance_detail, verbose_name=_("Name"))
    host = tables.Column("host", verbose_name=_("Host"))
    tor = tables.Column("remote_system_name", verbose_name=_("TOR"))
    network_name = tables.Column("network_name",
                                 verbose_name=_("Network Name"))
    local_vlan = tables.Column("local_vlan", verbose_name=_("Local Vlan"))
    vdp_vlan = tables.Column("vdp_vlan", verbose_name=_("Link Local Vlan"))
    seg_id = tables.Column("seg_id", verbose_name=_("Segmentation ID"))
    result = tables.Column(get_result, verbose_name=_("Result"))

    def get_object_id(self, obj):
        return obj.get('port_id')

    class Meta(object):
        name = "instancetable"
        hidden_title = False
        verbose_name = _("Instances")
        table_actions = (SearchFilterAction,)
        multi_select = False


class AgentsTable(tables.DataTable):
    host = tables.Column("host", verbose_name=_("Host"),
                         link='horizon:cisco:dfa:detail')
    created = tables.Column("created", verbose_name=_("Created"))
    heartbeat = tables.Column("heartbeat", verbose_name=_("Heartbeat"))
    agent_status = tables.Column("agent_status",
                                 verbose_name=_("Agent Status"))
    # lldpad_status = tables.Column("lldpad_status",
    #                              verbose_name=_("LLDP Daemon Status"))

    def get_object_id(self, obj):
        return obj.get('host')

    class Meta(object):
        name = "agentstable"
        verbose_name = _("Agents Table")
        table_actions = (SearchFilterAction,)
        multi_select = False


class TopologyTable(tables.DataTable):
    interface = tables.Column("interface", verbose_name=_("Interface"))
    remote_port = tables.Column("remote_port", verbose_name=_("Remote Port"))
    bond_intf = tables.Column("bond_intf", verbose_name=_("Bond Interface"))
    remote_evb_cfgd = tables.Column("remote_evb_cfgd",
                                    verbose_name=_("Remote EVB Configured"))
    remote_system_desc = tables.Column("remote_system_desc",
                                       verbose_name=_("Remote System"))
    remote_chassis_mac = tables.Column("remote_chassis_mac",
                                       verbose_name=_("Remote Chassis Mac"))
    remote_mgmt_addr = tables.Column("remote_mgmt_addr",
                                     verbose_name=_("Remote Mgmt Address"))
    remote_system_name = tables.Column("remote_system_name",
                                       verbose_name=_("Remote Sys Name"))
    remote_evb_mode = tables.Column("remote_evb_mode",
                                    verbose_name=_("Remote EVB Mode"))

    def get_object_id(self, obj):
        return obj.get('interface')

    class Meta(object):
        name = "topology"
        hidden_title = False
        verbose_name = _("Topology")
        multi_select = False
