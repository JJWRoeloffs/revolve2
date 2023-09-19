from ._joint_hinge import JointHinge


class ControlInterface:
    def set_joint_hinge_position_target(
        self, joint_hinge: JointHinge, position: float
    ) -> None:
        # raise NotImplementedError() TODO
        pass
