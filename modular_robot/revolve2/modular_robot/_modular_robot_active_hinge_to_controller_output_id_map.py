from revolve2.simulation.simulation_specification import JointHinge
from ._active_hinge import ActiveHinge
from revolve2.controllers import ControllerOutputId


class ModularRobotActiveHingeToControllerOutputIdMap:
    _inner_mapping: dict[int, ControllerOutputId]

    def __init__(self) -> None:
        self._inner_mapping = {}

    def add(
        self, active_hinge: ActiveHinge, controller_output_id: ControllerOutputId
    ) -> None:
        self._inner_mapping[id(active_hinge)] = controller_output_id

    def map(self, active_hinge: ActiveHinge) -> JointHinge:
        return self._inner_mapping[id(active_hinge)]
