from ._rigid_body import RigidBody
from ._hinge_joint import HingeJoint

from dataclasses import dataclass
import pyrr.aabb
from pyrr import Vector3
from ._aabb import AABB
from ._pose import Pose


@dataclass
class FreeObject:
    """
    An object in a physics simulation.

    Consists of multiple rigid bodies and joints connecting them.
    Must be a tree structure, meaning that every rigid body has a single joint parent
    and exactly one joint has zero parents.
    """

    pose: Pose
    """Pose of the object."""

    static: bool
    """Whether the object can move freely around, or if its root element is frozen and cannot move or rotate."""

    rigid_bodies: list[RigidBody]
    """The rigid bodies of the object."""

    hinge_joints: list[HingeJoint]
    """Hinges connecting bodies of the object."""

    def calc_aabb(self) -> tuple[Vector3, AABB]:
        """
        Calculate the axis aligned bounding box for this actor in 'T-pose', meaning all hinges are set to 0.

        This not the exact bounding box for the actor,
        but the smallest box the actor fits in that is aligned with the global axes.

        :returns: Position and AABB.
        """
        # List that will contain all corners of all convex geometries.
        points: list[Vector3] = []
        for body in self.rigid_bodies:
            for geometry in body.geometries:
                # Compute the absolute translation and rotation of the geometry.
                translation = body.position + body.orientation * geometry.position
                rotation = body.orientation * geometry.orientation

                # Iterate over all corners of the AABB and apply the translation and rotation.
                for x_sign in [1, -1]:
                    for y_sign in [1, -1]:
                        for z_sign in [1, -1]:
                            points.append(
                                translation
                                + rotation
                                * Vector3(
                                    x_sign * geometry.aabb.size.x,
                                    y_sign * geometry.aabb.size.y,
                                    z_sign * geometry.aabb.size.z,
                                )
                            )

        aabb = pyrr.aabb.create_from_points(points)
        minimum = Vector3(pyrr.aabb.minimum(aabb))
        maximum = Vector3(pyrr.aabb.maximum(aabb))

        return maximum - minimum, (maximum + minimum) / 2

        # xmin = 0
        # xmax = 0
        # ymin = 0
        # ymax = 0
        # zmin = 0
        # zmax = 0

        # for body in self.bodies:
        #     for collision in body.collisions:
        #         box = _Box(
        #             (
        #                 Vector3(
        #                     [
        #                         -collision.bounding_box.x,
        #                         -collision.bounding_box.y,
        #                         -collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         collision.bounding_box.x,
        #                         -collision.bounding_box.y,
        #                         -collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         -collision.bounding_box.x,
        #                         collision.bounding_box.y,
        #                         -collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         collision.bounding_box.x,
        #                         collision.bounding_box.y,
        #                         -collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         -collision.bounding_box.x,
        #                         -collision.bounding_box.y,
        #                         collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         collision.bounding_box.x,
        #                         -collision.bounding_box.y,
        #                         collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         -collision.bounding_box.x,
        #                         collision.bounding_box.y,
        #                         collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #                 Vector3(
        #                     [
        #                         collision.bounding_box.x,
        #                         collision.bounding_box.y,
        #                         collision.bounding_box.z,
        #                     ]
        #                 )
        #                 / 2.0,
        #             ),
        #         )
        #         box.rotate(collision.orientation)
        #         box.translate(collision.position)
        #         box.rotate(body.orientation)
        #         box.translate(body.position)

        #         aabb = box.aabb()
        #         xmax = max(xmax, aabb.offset.x + aabb.size.x / 2.0)
        #         ymax = max(ymax, aabb.offset.y + aabb.size.y / 2.0)
        #         zmax = max(zmax, aabb.offset.z + aabb.size.z / 2.0)
        #         xmin = min(xmin, aabb.offset.x - aabb.size.x / 2.0)
        #         ymin = min(ymin, aabb.offset.y - aabb.size.y / 2.0)
        #         zmin = min(zmin, aabb.offset.z - aabb.size.z / 2.0)

        # return BoundingBox(
        #     Vector3([xmax - xmin, ymax - ymin, zmax - zmin]),
        #     Vector3([(xmax + xmin) / 2.0, (ymax + ymin) / 2.0, (zmax + zmin) / 2.0]),
        # )


# _Coordinates: TypeAlias = tuple[
#     Vector3, Vector3, Vector3, Vector3, Vector3, Vector3, Vector3, Vector3
# ]


# @dataclass
# class _Box:
#     # The 8 coordinates of the box. Order is irrelevant.
#     coordinates: _Coordinates

#     def rotate(self, rotation: Quaternion) -> None:
#         self.coordinates = cast(
#             _Coordinates, tuple(rotation * coord for coord in self.coordinates)
#         )

#     def translate(self, offset: Vector3) -> None:
#         self.coordinates = cast(
#             _Coordinates, tuple(coord + offset for coord in self.coordinates)
#         )

#     def aabb(self) -> BoundingBox:
#         xmax = max([coord.x for coord in self.coordinates])
#         ymax = max([coord.y for coord in self.coordinates])
#         zmax = max([coord.z for coord in self.coordinates])
#         xmin = min([coord.x for coord in self.coordinates])
#         ymin = min([coord.y for coord in self.coordinates])
#         zmin = min([coord.z for coord in self.coordinates])
#         return BoundingBox(
#             Vector3([xmax - xmin, ymax - ymin, zmax - zmin]),
#             Vector3([(xmax + xmin) / 2.0, (ymax + ymin) / 2.0, (zmax + zmin) / 2.0]),
#         )
