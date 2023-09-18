from dataclasses import dataclass, field
from ._rigid_body import RigidBody
from ._joint import Joint
from ._pose import Pose
from pyrr import Vector3, Quaternion
from ._camera import Camera
from ._simulation_handler import SimulationHandler


@dataclass(kw_only=True)
class SimulationSpecification:
    ROOT = RigidBody(
        _is_root=True,
        name="root",
        pose=Pose(Vector3(), Quaternion()),
        static_friction=0.0,
        dynamic_friction=0.0,
    )

    handler: SimulationHandler

    bodies: list[RigidBody] = field(default_factory=list)
    joints: list[Joint] = field(default_factory=list)
    cameras: list[Camera] = field(default_factory=list)
