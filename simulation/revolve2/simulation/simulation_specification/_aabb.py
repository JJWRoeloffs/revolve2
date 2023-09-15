from pyrr import Vector3
from dataclasses import dataclass


@dataclass
class AABB:
    size: Vector3
    """
    Sizes of the length of the bounding box.
    
    Not half of the box.
    """
