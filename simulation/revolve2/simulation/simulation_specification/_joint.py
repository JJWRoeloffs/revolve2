from dataclasses import dataclass
from ._pose import Pose
from ._rigid_body import RigidBody


@dataclass
class Joint:
    """Base class for all joints."""

    name: str
    """Name of the joint."""

    pose: Pose
    """
    Pose of the joint.
    """

    body1: RigidBody
    """The first attached body."""

    body2: RigidBody
    """The second attached body."""
