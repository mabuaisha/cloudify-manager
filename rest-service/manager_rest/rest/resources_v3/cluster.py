#########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from manager_rest.security import MissingPremiumFeatureResource

from .. import rest_decorators, rest_utils
from ..responses_v3 import BaseResponse

try:
    from cloudify_premium import (ClusterResourceBase,
                                  ClusterState,
                                  ClusterNode)
except ImportError:
    ClusterNode, ClusterState = (BaseResponse, ) * 2
    ClusterResourceBase = MissingPremiumFeatureResource


class Cluster(ClusterResourceBase):
    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterState)
    @rest_decorators.create_filters()
    def get(self, cluster, _include=None, filters=None):
        """
        Current state of the cluster.
        """
        return cluster.cluster_status(_include=_include, filters=filters)

    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterState)
    def put(self, cluster):
        """
        Join the current manager to the cluster, or start a new one.

        If created, the cluster will already have one node (the current
        manager).
        """
        config = rest_utils.get_json_and_verify_params({
            'host_ip': {'type': unicode},
            'node_name': {'type': unicode},
            'join_addrs': {'type': list, 'optional': True},
            # opaque data - generated by the cluster, clients need
            # not examine it
            'credentials': {'optional': True},
        })
        if 'join_addrs' in config:
            return cluster.join(config)
        else:
            return cluster.start(config)

    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterState)
    def patch(self, cluster):
        """
        Update the cluster config.

        Use this to change settings or promote a replica machine to master.
        """
        config = rest_utils.get_json_and_verify_params()
        return cluster.update_config(config)


class ClusterNodes(ClusterResourceBase):
    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterNode)
    def get(self, cluster):
        """
        List the nodes in the current cluster.

        This will also list inactive nodes that weren't deleted. 404 if the
        cluster isn't created yet.
        """
        return cluster.list_nodes()


class ClusterNodesId(ClusterResourceBase):
    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterNode)
    def get(self, node_id, cluster):
        """
        Details of a node from the cluster.
        """
        return cluster.get_node(node_id)

    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterNode)
    def put(self, node_id, cluster):
        """Add a node to the cluster.

        Run validations, prepare credentials for that node to use.
        """
        details = rest_utils.get_json_and_verify_params({
            'host_ip': {'type': unicode},
            'node_name': {'type': unicode},
        })
        return cluster.add_node(details)

    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterState)
    def patch(self, node_id, cluster):
        """
        Update the config of this cluster node.

        Use this to change node-specific settings.
        """
        config = rest_utils.get_json_and_verify_params()
        return cluster.update_node_config(node_id, config)

    @rest_decorators.exceptions_handled
    @rest_decorators.marshal_with(ClusterNode)
    def delete(self, node_id, cluster):
        """
        Remove the node from the cluster.

        Use this when a node is permanently down.
        """
        return cluster.remove_node(node_id)
