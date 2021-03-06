########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import requests
import requests.status_codes
from requests.exceptions import ConnectionError

from cloudify_cli.env import get_auth_header

from integration_tests import AgentlessTestCase
from integration_tests.tests.utils import get_resource as resource


class ResourcesAvailableTest(AgentlessTestCase):

    def test_resources_available(self):
        container_ip = self.get_manager_ip()
        blueprint_id = 'b{0}'.format(uuid.uuid4())
        blueprint_name = 'empty_blueprint.yaml'
        blueprint_path = resource('dsl/{0}'.format(blueprint_name))
        self.client.blueprints.upload(blueprint_path,
                                      entity_id=blueprint_id)
        invalid_resource_url = 'https://{0}:{1}/resources/blueprints/{1}/{2}' \
            .format(container_ip, 53229, blueprint_id, blueprint_name)
        try:
            result = requests.head(invalid_resource_url)
            self.assertEqual(
                result.status_code, requests.status_codes.codes.not_found,
                "Resources are available through port 53229.")
        except ConnectionError:
            pass

    def test_resources_access(self):
        self.client.blueprints.upload(resource('dsl/empty_blueprint.yaml'),
                                      entity_id='blu')

        # admin can the blueprint
        admin_headers = self.client._client.headers
        self._assert_request_status_code(
            headers=admin_headers,
            path='/blueprints/default_tenant/blu/empty_blueprint.yaml',
            expected_status_code=requests.status_codes.codes.ok)

        # invalid authentication
        self._assert_request_status_code(
            headers=get_auth_header('bla', 'bla'),
            path='/blueprints/default_tenant/blu/empty_blueprint.yaml',
            expected_status_code=requests.status_codes.codes.unauthorized)

        # trying to access non-existing resource
        self._assert_request_status_code(
            headers=admin_headers,
            path='/blueprints/default_tenant/blu/non_existing_resource',
            expected_status_code=requests.status_codes.codes.not_found)

    def _assert_request_status_code(self,
                                    headers,
                                    path,
                                    expected_status_code):
        self.assertEquals(
            expected_status_code,
            requests.get(
                'https://{0}:53333/resources{1}'.format(self.get_manager_ip(),
                                                        path),
                headers=headers,
                verify=False
            ).status_code
        )
