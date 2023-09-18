from revolve2.simulation.simulation_specification import JointHinge
from ._active_hinge import ActiveHinge


class ModularRobotActiveHingeToSimulationJointHingeMap:
    _inner_mapping: dict[int, JointHinge]

    def __init__(self) -> None:
        self._inner_mapping = {}

    def add(self, from_active_hinge: ActiveHinge, to_joint_hinge: JointHinge) -> None:
        self._inner_mapping[id(from_active_hinge)] = to_joint_hinge

    def map(self, active_hinge: ActiveHinge) -> JointHinge:
        return self._inner_mapping[id(active_hinge)]
