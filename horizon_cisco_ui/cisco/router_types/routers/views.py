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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon_cisco_ui import api
from horizon_cisco_ui.cisco.router_types.routers import forms as routers_forms


class CreateView(forms.ModalFormView):
    modal_header = _("Create Router")
    form_class = routers_forms.CreateForm
    template_name = 'project/routers/create.html'
    success_url = reverse_lazy("horizon:cisco:router_types:index")
    submit_url = "horizon:cisco:router_types:routers:create"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['submit_url'] = \
            reverse(self.submit_url, args=(self.kwargs["router_type_id"],))
        return context

    def get_object(self):
        router_type_id = self.kwargs["router_type_id"]

        try:
            router_type = api.router_type_show(self.request, router_type_id)
            return router_type
        except Exception:
            msg = _("Unable to retrieve router type %s") % router_type_id
            exceptions.handle(self.request, msg, redirect=self.success_url)

    def get_initial(self):
        router_type = self.get_object()
        return {"router_type_id": router_type.id,
                "router_type_name": router_type.get('name')}
