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

from horizon_cisco_ui.cisco.asr1k.hosting_devices import tabs\
    as hosting_devices_tabs

from horizon_cisco_ui import api


class DetailView(tabs.TabView):
    tab_group_class = hosting_devices_tabs.DetailsTabs
    page_title = '{{ hosting_device_title }}'
    template_name = 'horizon/common/_detail.html'

    @memoized.memoized_method
    def _get_data(self):
        template_id = self.kwargs['hosting_device_id']
        try:
            hosting_device = api.hosting_device_show(self.request, template_id)
        except Exception:
            hosting_device = []
            msg = \
                _("Unable to retrieve details for hosting device %s")\
                % template_id
            exceptions.handle(self.request, msg)
        return hosting_device

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        breadcrumb = [
            (_("ASR1k"), reverse('horizon:cisco:asr1k:index')),
            (_("Hosting Device"),
             reverse('horizon:cisco:asr1k:hosting_devices')),
        ]

        context["custom_breadcrumb"] = breadcrumb
        hosting_device = self._get_data()
        context["hosting_device_title"] = \
            hosting_device.get('name', hosting_device['id'])
        return context

    def get_tabs(self, request, *args, **kwargs):
        hosting_device = self._get_data()
        return self.tab_group_class(request,
                                    hosting_device=hosting_device,
                                    **kwargs)
