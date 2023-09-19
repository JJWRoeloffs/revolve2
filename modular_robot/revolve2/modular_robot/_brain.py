from abc import ABC, abstractmethod

from revolve2.controllers import Controller
from ._controller_output_index_to_active_hinge_map import (
    ControllerOutputIndexToActiveHingeMap,
)


class Brain(ABC):
    """Interface for the brain of a modular robot."""

    @abstractmethod
    def make_controller(
        self,
    ) -> tuple[Controller, ControllerOutputIndexToActiveHingeMap]:
        pass
