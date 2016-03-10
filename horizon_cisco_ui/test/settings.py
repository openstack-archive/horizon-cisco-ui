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

# Small hack to ensure that the tests don't fail, due to the developer
# dashboard hitting settings
from horizon.utils import secret_key
import os
LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local')
SECRET_KEY = secret_key.generate_or_read_from_file(os.path.join(LOCAL_PATH,
                                                   '.secret_key_store'))

# Fall back to default o_d settings so we don't need to maintain our own
from openstack_dashboard.test.settings import *  # noqa
