from dataclasses import dataclass
from ._color import Color
from ._pose import Pose


@dataclass(kw_only=True)
class ConvexGeometry:
    """
    Convex geometry describing part of a rigid body shape.

    Currently always a box.
    """

    name: str
    """Name of the geometry."""

    pose: Pose
    """Pose of the geometry."""

    mass: float
    """
    Mass of the geometry.

    This the absolute mass, irrespective of the size of the bounding box.
    """

    color: Color
    """Color when rendering this geometry."""
