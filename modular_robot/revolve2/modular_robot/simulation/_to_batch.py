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
    AABB,
)
from revolve2.simulation.simulation_specification.geometry import GeometryBox
from ._modular_robot_simulation_specification import (
    ModularRobotSimulationSpecification,
    Terrain,
)
from .. import ActiveHinge, Module, Core, Brick, Body
from .._modular_robot_active_hinge_to_simulation_joint_hinge_map import (
    ModularRobotActiveHingeToSimulationJointHingeMap,
)
from pyrr import Vector3, Quaternion
import math
from revolve2.controllers import Controller
from .._brain import Brain
from .._modular_robot_active_hinge_to_controller_output_id_map import (
    ModularRobotActiveHingeToControllerOutputIdMap,
)
from .._controller_output_index_to_active_hinge_map import (
    ControllerOutputIndexToActiveHingeMap,
)


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

        terrain_bodies, terrain_joints = _prepare_terrain(
            simspec_robot.terrain, simspec.ROOT
        )
        simspec.bodies.extend(terrain_bodies)
        simspec.joints.extend(terrain_joints)

        converter = _BodyConverter()
        for robot_i, (robot, pose) in enumerate(simspec_robot.robots):
            (
                robot_bodies,
                robot_joints,
                active_hinge_to_joint_hinge_mapping,
            ) = converter._convert_robot_body(robot.body, pose, f"robot{robot_i}")

            handler.add_robot(robot.brain, active_hinge_to_joint_hinge_mapping)

            simspec.bodies.append(robot_bodies)
            simspec.joints.append(robot_joints)

        batch.simulation_specifications.append(simspec)

    return batch


def _prepare_terrain(
    terrain: Terrain, root_body: RigidBody
) -> tuple[list[RigidBody], list[Joint]]:
    body = RigidBody(
        name="terrain", pose=Pose(), static_friction=1.0, dynamic_friction=1.0
    )  # We use these friction values but in the future they should be set through the terrain description.
    for geometry in terrain.static_geometry:
        body.geometries.append(geometry)
    return [body], [JointFixed("terrain_joint_fixed", Pose(), root_body, body)]


class _ModularRobotSimulationHandler(SimulationHandler):
    _controllers: list[
        tuple[
            Controller,
            ModularRobotActiveHingeToSimulationJointHingeMap,
            ControllerOutputIndexToActiveHingeMap,
        ]
    ]

    def __init__(self) -> None:
        self._controllers = []

    def add_robot(
        self,
        brain: Brain,
        modular_robot_active_hinge_to_simulation_joint_hinge_mapping: ModularRobotActiveHingeToSimulationJointHingeMap,
    ) -> None:
        (
            controller,
            controller_output_index_to_active_hinge_mapping,
        ) = brain.make_controller()
        self._controllers.append(
            (
                controller,
                modular_robot_active_hinge_to_simulation_joint_hinge_mapping,
                controller_output_index_to_active_hinge_mapping,
            )
        )

    def setup(self, loaded_simulation: LoadedSimulation) -> None:
        pass

    def handle(
        self, state: SimulationState, control: ControlInterface, dt: float
    ) -> None:
        for (
            controller,
            modular_robot_active_hinge_to_simulation_joint_hinge_mapping,
            controller_output_index_to_active_hinge_mapping,
        ) in self._controllers:
            controller.step(dt)
            outputs = controller.get_outputs()
            for i, output in enumerate(outputs):
                joint_hinge = (
                    modular_robot_active_hinge_to_simulation_joint_hinge_mapping.map(
                        controller_output_index_to_active_hinge_mapping.map(i)
                    )
                )
                control.set_joint_hinge_position_target(joint_hinge, output)


class _BodyConverter:
    _STATIC_FRICTION = 1.0
    _DYNAMIC_FRICTION = 1.0

    bodies: list[RigidBody]
    joints: list[Joint]
    joint_mapping: ModularRobotActiveHingeToSimulationJointHingeMap

    def _convert_robot_body(
        self, body: Body, pose: Pose, base_name: str
    ) -> tuple[
        list[RigidBody], list[Joint], ModularRobotActiveHingeToSimulationJointHingeMap
    ]:
        self.bodies: list[RigidBody] = []
        self.joints: list[Joint] = []
        self.joint_mapping = ModularRobotActiveHingeToSimulationJointHingeMap()

        origin_body = RigidBody(
            name=f"{base_name}_origin",
            pose=pose,
            static_friction=self._STATIC_FRICTION,
            dynamic_friction=self._DYNAMIC_FRICTION,
        )
        self.bodies.append(origin_body)

        self._make_module(
            body.core,
            origin_body,
            f"{base_name}_origin",
            pose.position,
            pose.orientation,
        )

        return self.bodies, self.joints, self.joint_mapping

    def _make_module(
        self,
        module: Module,
        body: RigidBody,
        name_prefix: str,
        attachment_offset: Vector3,
        orientation: Quaternion,
    ) -> None:
        if isinstance(module, Core):
            self._make_core(
                module,
                body,
                name_prefix,
                attachment_offset,
                orientation,
            )
        elif isinstance(module, Brick):
            self._make_brick(
                module,
                body,
                name_prefix,
                attachment_offset,
                orientation,
            )
        elif isinstance(module, ActiveHinge):
            self._make_active_hinge(
                module,
                body,
                name_prefix,
                attachment_offset,
                orientation,
            )
        else:
            raise NotImplementedError("Module type not implemented")

    def _make_core(
        self,
        module: Core,
        body: RigidBody,
        name_prefix: str,
        attachment_point: Vector3,
        orientation: Quaternion,
    ) -> None:
        BOUNDING_BOX = Vector3([0.089, 0.089, 0.0603])  # meter
        MASS = 0.250  # kg
        CHILD_OFFSET = 0.089 / 2.0  # meter

        # attachment position is always at center of core
        position = attachment_point

        body.geometries.append(
            GeometryBox(
                pose=Pose(position, orientation),
                mass=MASS,
                color=module.color,
                aabb=AABB(BOUNDING_BOX),
            )
        )

        for name_suffix, child_index, angle in [
            ("front", Core.FRONT, 0.0),
            ("back", Core.BACK, math.pi),
            ("left", Core.LEFT, math.pi / 2.0),
            ("right", Core.RIGHT, math.pi / 2.0 * 3),
        ]:
            child = module.children[child_index]
            if child is not None:
                rotation = (
                    orientation
                    * Quaternion.from_eulers([0.0, 0.0, angle])
                    * Quaternion.from_eulers([child.rotation, 0, 0])
                )

                self._make_module(
                    child,
                    body,
                    f"{name_prefix}_{name_suffix}",
                    position + rotation * Vector3([CHILD_OFFSET, 0.0, 0.0]),
                    rotation,
                )

    def _make_brick(
        self,
        module: Brick,
        body: RigidBody,
        name_prefix: str,
        attachment_point: Vector3,
        orientation: Quaternion,
    ) -> None:
        BOUNDING_BOX = Vector3([0.06288625, 0.06288625, 0.0603])  # meter
        MASS = 0.030  # kg
        CHILD_OFFSET = 0.06288625 / 2.0  # meter

        position = attachment_point + orientation * Vector3(
            [BOUNDING_BOX[0] / 2.0, 0.0, 0.0]
        )

        body.geometries.append(
            GeometryBox(
                pose=Pose(position, orientation),
                mass=MASS,
                color=module.color,
                aabb=AABB(BOUNDING_BOX),
            )
        )

        for name_suffix, child_index, angle in [
            ("front", Brick.FRONT, 0.0),
            ("left", Brick.LEFT, math.pi / 2.0),
            ("right", Brick.RIGHT, math.pi / 2.0 * 3),
        ]:
            child = module.children[child_index]
            if child is not None:
                rotation = (
                    orientation
                    * Quaternion.from_eulers([0.0, 0.0, angle])
                    * Quaternion.from_eulers([child.rotation, 0, 0])
                )

                self._make_module(
                    child,
                    body,
                    f"{name_prefix}_{name_suffix}",
                    position + rotation * Vector3([CHILD_OFFSET, 0.0, 0.0]),
                    rotation,
                )

    def _make_active_hinge(
        self,
        module: ActiveHinge,
        body: RigidBody,
        name_prefix: str,
        attachment_point: Vector3,
        orientation: Quaternion,
    ) -> None:
        FRAME_BOUNDING_BOX = Vector3([0.018, 0.053, 0.0165891])  # meter
        FRAME_OFFSET = 0.04525
        SERVO1_BOUNDING_BOX = Vector3([0.0583, 0.0512, 0.020])  # meter
        SERVO2_BOUNDING_BOX = Vector3([0.002, 0.053, 0.053])  # meter

        FRAME_MASS = 0.011  # kg
        SERVO1_MASS = 0.058  # kg
        SERVO2_MASS = 0.02  # kg. we simplify by only using the weight of the first box

        SERVO_OFFSET = 0.0299  # meter. distance from frame to servo
        JOINT_OFFSET = 0.0119  # meter. distance from frame to joint

        SERVO_BBOX2_POSITION = Vector3(
            [SERVO1_BOUNDING_BOX[0] / 2.0 + SERVO2_BOUNDING_BOX[0] / 2.0, 0.0, 0.0]
        )

        ATTACHMENT_OFFSET = SERVO1_BOUNDING_BOX[0] / 2.0 + SERVO2_BOUNDING_BOX[0]

        frame_position = attachment_point + orientation * Vector3(
            [FRAME_OFFSET / 2.0, 0.0, 0.0]
        )
        frame_position_real = attachment_point + orientation * Vector3(
            [FRAME_BOUNDING_BOX[0] / 2.0, 0.0, 0.0]
        )
        servo_body_position = body.pose.position + body.pose.orientation * (
            frame_position + orientation * Vector3([SERVO_OFFSET, 0.0, 0.0])
        )
        servo_body_orientation = body.pose.orientation * orientation
        joint_position = body.pose.position + body.pose.orientation * (
            frame_position + orientation * Vector3([JOINT_OFFSET, 0.0, 0.0])
        )
        joint_orientation = body.pose.orientation * orientation

        body.geometries.append(
            GeometryBox(
                pose=Pose(frame_position_real, orientation),
                mass=FRAME_MASS,
                color=module.color,
                aabb=AABB(FRAME_BOUNDING_BOX),
            )
        )

        next_body = RigidBody(
            name=f"{name_prefix}_activehinge",
            pose=Pose(servo_body_position, servo_body_orientation),
            static_friction=self._STATIC_FRICTION,
            dynamic_friction=self._DYNAMIC_FRICTION,
        )
        self.bodies.append(next_body)
        joint = JointHinge(
            name=f"{name_prefix}_activehinge",
            pose=Pose(joint_position, joint_orientation),
            body1=body,
            body2=next_body,
            axis=Vector3([0.0, 1.0, 0.0]),
            range=module.RANGE,
            effort=module.EFFORT,
            velocity=module.VELOCITY,
        )
        self.joints.append(joint)
        self.joint_mapping.add(module, joint)

        next_body.geometries.append(
            GeometryBox(
                pose=Pose(Vector3(), Quaternion()),
                mass=SERVO1_MASS,
                color=module.color,
                aabb=AABB(SERVO1_BOUNDING_BOX),
            )
        )
        next_body.geometries.append(
            GeometryBox(
                pose=Pose(SERVO_BBOX2_POSITION, Quaternion()),
                mass=SERVO2_MASS,
                color=module.color,
                aabb=AABB(SERVO2_BOUNDING_BOX),
            )
        )

        child = module.children[ActiveHinge.ATTACHMENT]
        if child is not None:
            rotation = Quaternion.from_eulers([child.rotation, 0.0, 0.0])

            self._make_module(
                child,
                next_body,
                f"{name_prefix}_attachment",
                rotation * Vector3([ATTACHMENT_OFFSET, 0.0, 0.0]),
                rotation,
            )
