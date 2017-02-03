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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon_cisco_ui.cisco.dfa import dfa_client

LOG = logging.getLogger(__name__)


class AssociateDCI(forms.SelfHandlingForm):
    project_id = forms.CharField(label=_("Project ID "),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}))
    dci_id = forms.IntegerField(label=_("DCI ID"), min_value=1,
                                max_value=1600000)

    def handle(self, request, data):
        try:
            LOG.debug('request = %(req)s, params = %(params)s',
                      {'req': request, 'params': data})
            tenant = dict(tenant_id=request.user.project_id,
                          tenant_name=request.user.project_name,
                          dci_id=data['dci_id'])
            dfa_client.do_associate_dci_id_to_project(tenant)
        except Exception:
            redirect = reverse('horizon:cisco:dfa:index')
            msg = _('Failed to associate DCI ID to project')
            exceptions.handle(request, msg, redirect=redirect)

        return True


class DisassociateDCI(forms.SelfHandlingForm):

    def handle(self, request, data):
        try:
            LOG.debug('request = %(req)s, params = %(params)s',
                      {'req': request, 'params': data})
            tenant = dict(tenant_id=request.user.project_id,
                          tenant_name=request.user.project_name,
                          dci_id=0)
            dfa_client.do_associate_dci_id_to_project(tenant)
        except Exception:
            redirect = reverse('horizon:cisco:dfa:index')
            msg = _('Failed to disassociate DCI ID from project')
            exceptions.handle(request, msg, redirect=redirect)

        return True
