from pyrr import Vector3, Quaternion
from dataclasses import dataclass


@dataclass
class Pose:
    position: Vector3
    orientation: Quaternion
