from dataclasses import dataclass, field
from ._pose import Pose
from ._geometry import Geometry


@dataclass
class RigidBody:
    """A collection of geometries and physics parameters."""

    _is_root: bool = False
    """Whether this is the root rigid body of the simulation."""

    name: str
    """Name of the rigid body."""

    pose: Pose
    """Pose of the rigid body."""

    static_friction: float
    """Static friction of the body."""

    dynamic_friction: float
    """Dynamic friction of the body."""

    geometries: list[Geometry] = field(default_factory=list, init=False)
    """Geometries describing the shape of the body."""
