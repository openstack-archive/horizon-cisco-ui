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

from django.utils.translation import ugettext_lazy as _

import horizon
from horizon_cisco_ui.cisco import dashboard
import logging
import os.path

LOG = logging.getLogger(__name__)


class DFA(horizon.Panel):
    name = _("Programmable Fabric")
    slug = "dfa"
    permissions = ('openstack.services.network',)

    def allowed(self, context):
        request = context['request']
        if not request.user.has_perms(self.permissions):
            return False
        try:
            if not os.path.isfile('/etc/saf/enabler_conf.ini'):
                return False
        except Exception:
            LOG.error("Exception occured trying to find the Nexus Fabric "
                      "Enabler Configuration File")
            return False
        if not super(DFA, self).allowed(context):
            return False
        return True

dashboard.Cisco.register(DFA)
