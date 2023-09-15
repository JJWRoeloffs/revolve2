from abc import ABC, abstractmethod
from ._simulation_state import SimulationState
from ._loaded_simulation import LoadedSimulation
from ._control_interface import ControlInterface


class SimulationHandler(ABC):
    """Base class for handling a simulation, which includes, for example, controlling robots."""

    @abstractmethod
    def setup(self, loaded_simulation: LoadedSimulation) -> None:
        """
        Set up everything that only needs to be done once.

        For example, getting control identifiers for joints that need to be moved.

        :param loaded_simulation: Interface for getting information about the loaded simulation.
        This could, for instance, be used to get an idenfier for a joint that can be used later to control that joint.
        """
        pass

    @abstractmethod
    def handle(self, state: SimulationState, control: ControlInterface) -> None:
        """
        Handle a simulation frame

        :param state: The current state of the simulation.
        :param control: Interface for setting control targets.
        """
        pass
