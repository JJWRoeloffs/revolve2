from __future__ import annotations

import numpy as np
import numpy.typing as npt
from revolve2.controllers import Controller
from .._controller_output_index_to_active_hinge_map import (
    ControllerOutputIndexToActiveHingeMap,
)
from revolve2.controllers.cpg import ControllerCpg, CpgNetworkStructure
from revolve2.modular_robot import Brain


class BrainCpgNetworkStatic(Brain):
    """
    A CPG brain with cpgs and connections defined by the user.

    A state vector is integrated over time using a weight matrix which multiplication with the state vector sum defines the derivative of the state vector.
    I.e X' = WX

    The first `num_output_neurons` in the state vector are the outputs for the controller created by this brain.
    """

    _initial_state: npt.NDArray[np.float_]
    _weight_matrix: npt.NDArray[np.float_]
    _dof_ranges: npt.NDArray[np.float_]
    _outputs: list[int]

    def __init__(
        self,
        initial_state: npt.NDArray[np.float_],
        weight_matrix: npt.NDArray[np.float_],
        dof_ranges: npt.NDArray[np.float_],
        outputs: list[int],
    ) -> None:
        """
        Initialize this object.

        :param initial_state: The initial state of the neural network.
        :param weight_matrix: The weight matrix used during integration.
        :param dof_ranges: Maximum range (half the complete range) of the output of degrees of freedom.
        :param outputs: Marks neurons as controller outputs. `get_outputs` will return the values of these neurons, in order of this parameter.
        """
        self._initial_state = initial_state
        self._weight_matrix = weight_matrix
        self._dof_ranges = dof_ranges
        self._outputs = outputs

    @classmethod
    def create_simple(
        cls,
        params: npt.NDArray[np.float_],
        cpg_network_structure: CpgNetworkStructure,
        initial_state_uniform: float,
        dof_range_uniform: float,
    ) -> BrainCpgNetworkStatic:
        """
        Create and initialize an instance of this brain using a simplified interface.

        :param params: Parameters for the weight matrix to be created.
        :param cpg_network_structure: The cpg network structure.
        :param initial_state_uniform: Initial state to use for all neurons.
        :param dof_range_uniform: Dof range to use for all neurons.
        :returns: The created brain.
        """
        initial_state = cpg_network_structure.make_uniform_state(initial_state_uniform)
        weight_matrix = (
            cpg_network_structure.make_connection_weights_matrix_from_params(
                list(params)
            )
        )
        dof_ranges = cpg_network_structure.make_uniform_dof_ranges(dof_range_uniform)
        return BrainCpgNetworkStatic(
            initial_state=initial_state,
            weight_matrix=weight_matrix,
            dof_ranges=dof_ranges,
            outputs=cpg_network_structure.output_indices,
        )

    def make_controller(
        self,
    ) -> tuple[Controller, ControllerOutputIndexToActiveHingeMap]:
        return ControllerCpg(
            initial_state=self._initial_state,
            weight_matrix=self._weight_matrix,
            dof_ranges=self._dof_ranges,
            outputs=self._outputs,
        )
