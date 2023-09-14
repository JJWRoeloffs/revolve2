from ._convex_geometry import ConvexGeometry

from dataclasses import dataclass, field
from ._pose import Pose


@dataclass
class RigidBody:
    """A rigid body with a shape described by multiple convex geometries."""

    name: str
    """Name of the rigid body."""

    pose: Pose
    """Pose of the rigid body."""

    static_friction: float
    """Static friction of the body."""

    dynamic_friction: float
    """Dynamic friction of the body."""

    geometries: list[ConvexGeometry] = field(default_factory=list, init=False)
    """Geometries describing the shape of the body."""
