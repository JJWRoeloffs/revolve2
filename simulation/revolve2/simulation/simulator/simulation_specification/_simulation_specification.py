from dataclasses import dataclass, field
from ._rigid_body import RigidBody
from ._joint import Joint
from ._pose import Pose
from pyrr import Vector3, Quaternion
from ._camera import Camera


@dataclass
class SimulationSpecification:
    _root: RigidBody = field(
        default_factory=lambda: RigidBody(
            _is_root=True,
            name="root",
            pose=Pose(Vector3(), Quaternion()),
            static_friction=0.0,
            dynamic_friction=0.0,
        )
    )

    @property
    def root(self) -> RigidBody:
        return self._root

    bodies: list[RigidBody] = field(default=list)
    joints: list[Joint] = field(default=list)
    cameras: list[Camera] = field(default=list)
