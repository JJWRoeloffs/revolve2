from abc import ABC, abstractmethod

from revolve2.actor_controller import ActorController
from ._modular_robot_active_hinge_to_simulation_joint_hinge_map import (
    ModularRobotActiveHingeToSimulationJointHingeMap,
)
from ._dof_id_to_simulation_joint_hinge_map import DofIdToSimulationJointHingeMap


class Brain(ABC):
    """Interface for the brain of a modular robot."""

    @abstractmethod
    def make_controller(
        self,
        modular_robot_active_hinge_to_simulation_joint_hinge_mapping: ModularRobotActiveHingeToSimulationJointHingeMap,
    ) -> tuple[ActorController, DofIdToSimulationJointHingeMap]:
        pass
