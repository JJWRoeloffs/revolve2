import math
from abc import ABC, abstractmethod

from revolve2.controllers import Controller
from revolve2.controllers.cpg import ControllerCpg
from revolve2.modular_robot import ActiveHinge, Body, Brain

from ._make_cpg_network_structure_neighbor import (
    active_hinges_to_cpg_network_structure_neighbor,
)
from .._controller_output_index_to_active_hinge_map import (
    ControllerOutputIndexToActiveHingeMap,
)


class BrainCpgNetworkNeighbor(Brain, ABC):
    """
    A CPG brain with active hinges that are connected if they are within 2 jumps in the modular robot tree structure.

    That means, NOT grid coordinates, but tree distance.
    """

    _body: Body

    def __init__(self, body: Body) -> None:
        self._body = body

    def make_controller(
        self,
    ) -> tuple[Controller, ControllerOutputIndexToActiveHingeMap]:
        active_hinges = self._body.find_active_hinges()

        cpg_network_structure = active_hinges_to_cpg_network_structure_neighbor(
            active_hinges
        )
        connections = [
            (
                active_hinges[pair.cpg_index_lowest.index],
                active_hinges[pair.cpg_index_highest.index],
            )
            for pair in cpg_network_structure.connections
        ]

        (internal_weights, external_weights) = self._make_weights(
            active_hinges, connections, self._body
        )
        weight_matrix = cpg_network_structure.make_connection_weights_matrix(
            {
                cpg: weight
                for cpg, weight in zip(cpg_network_structure.cpgs, internal_weights)
            },
            {
                pair: weight
                for pair, weight in zip(
                    cpg_network_structure.connections, external_weights
                )
            },
        )
        initial_state = cpg_network_structure.make_uniform_state(0.5 * math.sqrt(2))
        dof_ranges = cpg_network_structure.make_uniform_dof_ranges(1.0)

        output_indices = cpg_network_structure.output_indices

        index_map = ControllerOutputIndexToActiveHingeMap()
        for i, active_hinge in enumerate(active_hinges):
            index_map.add(i, active_hinge)

        return (
            ControllerCpg(
                initial_state=initial_state,
                weight_matrix=weight_matrix,
                dof_ranges=dof_ranges,
                outputs=output_indices,
            ),
            index_map,
        )

    @abstractmethod
    def _make_weights(
        self,
        active_hinges: list[ActiveHinge],
        connections: list[tuple[ActiveHinge, ActiveHinge]],
        body: Body,
    ) -> tuple[list[float], list[float]]:
        """
        Define the weights between neurons.

        :param active_hinges: The active hinges corresponding to each cpg.
        :param connections: Pairs of active hinges corresponding to pairs of cpgs that are connected.
                            Connection is from hinge 0 to hinge 1.
                            Opposite connection is not provided as weights are assumed to be negative.
        :param body: The body that matches this brain.
        :returns: Two lists. The first list contains the internal weights in cpgs, corresponding to `active_hinges`
                 The second list contains the weights between connected cpgs, corresponding to `connections`
                 The lists should match the order of the input parameters.
        """
