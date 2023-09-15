from revolve2.simulation.simulator import Batch, BatchParameters
from ._modular_robot_simulation_specification import ModularRobotSimulationSpecification


def ToBatch(
    simulation_specification: ModularRobotSimulationSpecification
    | list[ModularRobotSimulationSpecification],
) -> Batch:
    raise NotImplementedError()
