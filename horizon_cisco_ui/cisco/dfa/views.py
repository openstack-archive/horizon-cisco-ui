# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

import json
import logging
import re

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized
from horizon import views

from horizon_cisco_ui.cisco.dfa import dfa_client
from horizon_cisco_ui.cisco.dfa import forms as dfaforms
from horizon_cisco_ui.cisco.dfa import tables as dfatables
from horizon_cisco_ui.cisco.dfa import tabs as dfatab

LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    tab_group_class = dfatab.DFATabs
    template_name = 'cisco/dfa/index.html'
    page_title = _("Programmable Fabric")


class AssociateDCIToProjectView(forms.ModalFormView):
    form_class = dfaforms.AssociateDCI
    form_id = "associate_form"
    modal_header = _("Associate DCI ID to Project")
    template_name = 'cisco/dfa/associate.html'
    submit_label = _("ASSOCIATE")
    submit_url = "horizon:cisco:dfa:associate"
    success_url = reverse_lazy('horizon:cisco:dfa:index')
    page_title = _("ASSOCIATE DCI ID")

    def get_context_data(self, **kwargs):
        context = super(AssociateDCIToProjectView,
                        self).get_context_data(**kwargs)
        args = (self.kwargs['project_id'],)
        context["project_id"] = self.kwargs['project_id']
        context["submit_url"] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        return self.kwargs["project_id"]

    def get_initial(self):
        return {'project_id': self._get_object()}


class DisssociateDCIToProjectView(forms.ModalFormView):
    form_class = dfaforms.DisassociateDCI
    form_id = "disassociate_form"
    modal_header = _("Disassociate DCI ID to Project")
    template_name = 'cisco/dfa/disassociate.html'
    submit_label = _("DISASSOCIATE")
    submit_url = "horizon:cisco:dfa:disassociate"
    success_url = reverse_lazy('horizon:cisco:dfa:index')

    def get_context_data(self, **kwargs):
        context = super(DisssociateDCIToProjectView,
                        self).get_context_data(**kwargs)
        args = (self.kwargs['project_id'],)
        context["project_id"] = self.kwargs['project_id']
        context["submit_url"] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        return self.kwargs["project_id"]

    def get_initial(self):
        return {'project_id': self._get_object()}


class DetailProfileView(views.HorizonTemplateView):
    template_name = 'cisco/dfa/detailprofile.html'
    page_title = "{{ profile_name }}"

    def get_context_data(self, **kwargs):
        context = super(DetailProfileView, self).get_context_data(**kwargs)
        data = self._get_data()
        rep = {'\r': '<br>', ' ': '&nbsp;'}
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        commands = pattern.sub(lambda m: rep[re.escape(m.group(0))],
                               data.get('configCommands'))
        context['Profile_Name'] = self.kwargs['profile_name'].split(":")[0]
        context['Profile_Type'] = self.kwargs['profile_name'].split(":")[1]
        context['fwding_mode'] = data.get('forwardingMode')
        context['description'] = data.get('description')
        context['commands'] = commands

        return context

    @memoized.memoized_method
    def _get_data(self):
        try:
            profile_name = self.kwargs['profile_name']
            cfg_profile = {'profile': profile_name.split(":")[0],
                           'ftype': profile_name.split(":")[1]}
            data = dfa_client.get_per_config_profile_detail(cfg_profile)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve host details.'),
                              redirect=self.get_redirect_url())
        return data

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:cisco:dfa:index')


class DetailView(tables.MultiTableView):
    table_classes = (dfatables.TopologyTable, )
    template_name = 'cisco/dfa/detail.html'
    page_title = "{{ agent.host }}"

    def get_topology_data(self):
        try:
            topology = []
            agent = self._get_data()
            cfg = json.loads(agent.get('config'))
            topo = cfg.get('topo')
            for key in topo.keys():
                intf = topo.get(key)
                if not intf.get('remote_evb_cfgd'):
                    continue
                topology.append(
                    dict(
                        interface=cfg.get('uplink'),
                        remote_port=intf.get('remote_port'),
                        bond_intf=intf.get('bond_intf'),
                        remote_port_mac=intf.get('remote_port_id_mac'),
                        remote_evb_cfgd=intf.get('remote_evb_cfgd'),
                        remote_system_desc=intf.get('remote_system_desc'),
                        remote_chassis_mac=intf.get('remote_chassis_id_mac'),
                        remote_mgmt_addr=intf.get('remote_mgmt_addr'),
                        remote_system_name=intf.get('remote_system_name'),
                        remote_evb_mode=intf.get('remote_evb_mode')))
        except Exception:
            topology = []
            msg = _('Neighborship is not established for this server')
            exceptions.handle(self.request, msg)
        return topology

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        agent = self._get_data()
        context["agent"] = agent
        cfg = json.loads(agent.get('config'))
        context["uplink"] = cfg.get('uplink')
        context["memb_ports"] = cfg.get('memb_ports')
        context["veth_intf"] = cfg.get('veth_intf')
        context["url"] = self.get_redirect_url()
        return context

    @memoized.memoized_method
    def _get_data(self):
        try:
            host_name = self.kwargs['host']
            NFEhost = dict(host=host_name)
            agent = (dfa_client.get_agent_details_per_host(NFEhost))[0]
            agent["heartbeat"] = agent.get('heartbeat').replace('T', ' ')[:-7]
            agent["created"] = agent.get('created').replace('T', ' ')[:-7]
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve host details.'),
                              redirect=self.get_redirect_url())
        return agent

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:cisco:dfa:index')
