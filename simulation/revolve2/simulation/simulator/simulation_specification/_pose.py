from pyrr import Vector3, Quaternion
from dataclasses import dataclass


@dataclass
class Pose:
    """A position and orientation."""

    position: Vector3
    """Position of the object."""

    orientation: Quaternion
    """Orientation of the object."""
