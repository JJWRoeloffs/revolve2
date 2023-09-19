from __future__ import annotations

import numpy as np
import numpy.typing as npt
from .._controller import Controller
from .._controller_output_id import ControllerOutputId


class ControllerCpg(Controller):
    """
    Cpg network brain.

    A state array that is integrated over time following the differential equation `X'=WX`.
    W is a weight matrix that is multiplied by the state array.
    The first `num_output_neurons` are the degree of freedom outputs of the controller.
    """

    _initial_state: npt.NDArray[np.float_]
    _weight_matrix: npt.NDArray[np.float_]  # nxn matrix matching number of neurons
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
        assert initial_state.ndim == 1
        assert weight_matrix.ndim == 2
        assert weight_matrix.shape[0] == weight_matrix.shape[1]
        assert initial_state.shape[0] == weight_matrix.shape[0]

        self._state = initial_state
        self._weight_matrix = weight_matrix
        self._dof_ranges = dof_ranges
        self._outputs = outputs

    def step(self, dt: float) -> None:
        """
        Step the controller dt seconds forward.

        :param dt: The number of seconds to step forward.
        """
        self._state = self._rk45(self._state, self._weight_matrix, dt)

    @staticmethod
    def _rk45(
        state: npt.NDArray[np.float_], A: npt.NDArray[np.float_], dt: float
    ) -> npt.NDArray[np.float_]:
        A1: npt.NDArray[np.float_] = np.matmul(A, state)
        A2: npt.NDArray[np.float_] = np.matmul(A, (state + dt / 2 * A1))
        A3: npt.NDArray[np.float_] = np.matmul(A, (state + dt / 2 * A2))
        A4: npt.NDArray[np.float_] = np.matmul(A, (state + dt * A3))
        return state + dt / 6 * (A1 + 2 * (A2 + A3) + A4)

    def get_outputs(self) -> list[float]:
        """
        Get the outputs of the controller.

        :returns: The outputs of the controller paired with the identifier of that control output.
        """
        return np.clip(
            self._state[self._outputs],
            a_min=-self._dof_ranges,
            a_max=self._dof_ranges,
        )
