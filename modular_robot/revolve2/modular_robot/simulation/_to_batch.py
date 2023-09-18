from revolve2.simulation.simulator import Batch, BatchParameters, RecordSettings
from revolve2.simulation.simulation_specification import (
    SimulationSpecification,
    RigidBody,
    SimulationHandler,
    Joint,
    JointFixed,
    JointHinge,
    Pose,
    LoadedSimulation,
    SimulationState,
    ControlInterface,
)
from ._modular_robot_simulation_specification import (
    ModularRobotSimulationSpecification,
    Terrain,
    ModularRobot,
)
from .. import ActiveHinge, Brain


def to_batch(
    simulation_specifications: ModularRobotSimulationSpecification
    | list[ModularRobotSimulationSpecification],
    batch_parameters: BatchParameters,
    record_settings: RecordSettings | None = None,
) -> Batch:
    if isinstance(simulation_specifications, ModularRobotSimulationSpecification):
        simulation_specifications = [simulation_specifications]
    batch = Batch(parameters=batch_parameters, record_settings=record_settings)

    for simspec_robot in simulation_specifications:
        handler = _ModularRobotSimulationHandler()
        simspec = SimulationSpecification(handler=handler)

        (terrain_bodies, terrain_joints) = _prepare_terrain(
            simspec_robot.terrain, simspec.root
        )
        simspec.bodies.append(terrain_bodies)
        simspec.joints.append(terrain_joints)

        for robot, pose in simspec_robot.robots:
            (
                robot_bodies,
                robot_joints,
                active_hinge_to_joint_hinge_mapping,
            ) = _prepare_robot_body(robot.body, pose)

            handler.add_robot(robot.brain, active_hinge_to_joint_hinge_mapping)

            simspec.bodies.append(robot_bodies)
            simspec.joints.append(robot_joints)

        batch.simulation_specifications.append(simspec)

    return batch


def _prepare_terrain(
    terrain: Terrain, root_body: RigidBody
) -> tuple[list[RigidBody], list[Joint]]:
    raise NotImplementedError()


class _ActiveHingeToJointHingeMap:
    _inner_mapping: dict[int, JointHinge]

    def map(self, active_hinge: ActiveHinge) -> JointHinge:
        return self._inner_mapping[id(active_hinge)]


def _prepare_robot_body(
    robot: ModularRobot, pose: Pose
) -> tuple[list[RigidBody], list[Joint], _ActiveHingeToJointHingeMap]:
    raise NotImplementedError()


class _ModularRobotSimulationHandler(SimulationHandler):
    def add_robot(
        brain: Brain, active_hinge_to_joint_hinge_map: _ActiveHingeToJointHingeMap
    ) -> None:
        raise NotImplementedError()

    def setup(self, loaded_simulation: LoadedSimulation) -> None:
        NotImplementedError()

    def handle(self, state: SimulationState, control: ControlInterface) -> None:
        NotImplementedError()
