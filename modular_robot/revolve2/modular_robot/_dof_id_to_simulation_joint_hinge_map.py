from revolve2.simulation.simulation_specification import JointHinge
from ._active_hinge import ActiveHinge


class DofIdToSimulationJointHingeMap:
    _inner_mapping: dict[int, JointHinge]

    def __init__(self) -> None:
        self._inner_mapping = {}

    def add(self, dof_id: int, to_joint_hinge: JointHinge) -> None:
        self._inner_mapping[dof_id] = to_joint_hinge

    def map(self, dof_id: int) -> JointHinge:
        return self._inner_mapping[dof_id]
