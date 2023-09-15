from dataclasses import dataclass
from ._geometry import Geometry
from pyrr import Vector3


@dataclass(kw_only=True)
class GeometryPlane(Geometry):
    """A flat plane geometry."""

    size: Vector3  # z is ignored because a plane has 0 thickness
    color: Vector3 = Vector3([0.2, 0.2, 0.2])
