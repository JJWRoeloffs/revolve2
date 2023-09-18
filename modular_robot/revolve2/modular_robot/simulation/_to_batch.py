from revolve2.simulation.simulator import Batch, BatchParameters
from ._modular_robot_simulation_specification import ModularRobotSimulationSpecification


def to_batch(
    simulation_specification: ModularRobotSimulationSpecification
    | list[ModularRobotSimulationSpecification],
    batch_parameters: BatchParameters,
) -> Batch:
    if isinstance(simulation_specification, ModularRobotSimulationSpecification):
        simulation_specification = [simulation_specification]
    raise NotImplementedError()
