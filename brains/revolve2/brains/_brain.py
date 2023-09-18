from __future__ import annotations

from abc import ABC, abstractmethod
from ._controller_output_id import ControllerOutputId


class Brain(ABC):
    """Interface for brains, which is another word for 'controller'."""

    @abstractmethod
    def step(self, dt: float) -> None:
        """
        Step the controller dt seconds forward.

        :param dt: The number of seconds to step forward.
        """
        pass

    @abstractmethod
    def get_outputs(self) -> list[tuple[ControllerOutputId, float]]:
        """
        Get the outputs of the controller.

        :returns: The outputs of the controller paired with the identifier of that control output.
        """
        pass
