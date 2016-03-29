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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon.utils import memoized

from horizon_cisco_ui.cisco.device_management.hosting_device_templates \
    import tabs as hosting_device_templates_tabs

from horizon_cisco_ui import api


class DetailView(tabs.TabView):
    tab_group_class = hosting_device_templates_tabs.DetailsTabs
    page_title = '{{ device_template_title }}'
    template_name = 'horizon/common/_detail.html'

    @memoized.memoized_method
    def _get_data(self):
        template_id = self.kwargs['hosting_device_template_id']
        try:
            hosting_device_template =\
                api.hosting_device_template_show(self.request, template_id)
        except Exception:
            hosting_device_template = {}
            msg = \
                _("Unable to retrieve details for hosting device template %s")\
                % template_id
            exceptions.handle(self.request, msg)
        return hosting_device_template

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        device_template_url = \
            reverse('horizon:cisco:device_management:hosting_device_templates')
        breadcrumb = [
            (_("Device Management"),
             reverse('horizon:cisco:device_management:index')),
            (_("Device Templates"), device_template_url),
        ]

        context["custom_breadcrumb"] = breadcrumb
        device_template = self._get_data()
        context["device_template_title"] = \
            device_template.get('name', device_template['id'])
        return context

    def get_tabs(self, request, *args, **kwargs):
        device_template = self._get_data()
        return self.tab_group_class(request,
                                    device_template=device_template,
                                    **kwargs)
