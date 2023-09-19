from pyrr import Quaternion, Vector3
from revolve2.controllers import Brain

from ._environment_controller import EnvironmentBrain
from ._terrain import Terrain
from .actor import Actor
from .running import Environment, PosedActor


def create_environment_single_actor(
    actor: Actor, controller: Brain, terrain: Terrain
) -> Environment:
    """
    Create an environment for simulating a single actor.

    :param actor: The actor to simulate.
    :param controller: The controller for the actor.
    :param terrain: The terrain to simulate the actor in.
    :returns: The created environment.
    """
    bounding_box = actor.calc_aabb()

    env = Environment(EnvironmentBrain(controller))
    env.static_geometries.extend(terrain.static_geometry)
    env.actors.append(
        PosedActor(
            actor,
            Vector3(
                [
                    0.0,
                    0.0,
                    bounding_box.size.z / 2.0 - bounding_box.offset.z,
                ]
            ),
            Quaternion(),
            [0.0 for _ in controller.get_dof_targets()],
        )
    )
    return env
