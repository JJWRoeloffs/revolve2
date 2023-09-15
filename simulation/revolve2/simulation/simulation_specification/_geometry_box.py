from dataclasses import dataclass
from ._aabb import AABB
from ._convex_geometry import ConvexGeometry


@dataclass(kw_only=True)
class GeometryBox(ConvexGeometry):
    """Box convex geometry."""

    aabb: AABB
    """AABB describing the box's shape."""
