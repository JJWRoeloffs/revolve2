from .._modular_robot import ModularRobot
from dataclasses import dataclass, field
from revolve2.simulation.simulation_specification import Pose, SimulationSpecification
from ._terrain import Terrain


@dataclass
class ModularRobotSimulationSpecification:
    terrain: Terrain
    robots: list[tuple[ModularRobot, Pose]] = field(default_factory=list)

    def add_robot(self, robot: ModularRobot, pose: Pose = Pose()) -> None:
        self.robots.append((robot, pose))

    def to_simulation_specification(self) -> SimulationSpecification:
        raise NotImplementedError()
