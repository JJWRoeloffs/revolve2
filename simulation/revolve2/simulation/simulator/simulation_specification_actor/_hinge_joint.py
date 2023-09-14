from ._rigid_body import RigidBody

from dataclasses import dataclass
from pyrr import Vector3
from ._pose import Pose


@dataclass
class HingeJoint:
    """
    A hinge joint between a parent and child body.

    Also known as revolute joint.
    It rotates around a single axis.
    """

    name: str
    """Name of the joint."""

    parent_body: RigidBody
    """The parent body."""

    child_body: RigidBody
    """The child body."""

    pose: Pose
    """
    Pose of the joint.
    """

    axis: Vector3
    """Directional vector the joint rotates about."""

    range: float
    """
    Rotation range of the joint in radians.
    
    How much it can rotate to each side, in radians.
    So double this is the complete range of motion.
    """

    effort: float
    """Maximum effort the joint can exert, in newton-meter."""

    velocity: float
    """Maximum velocity of the joint, in radian per second."""
