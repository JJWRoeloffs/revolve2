from .._simulation_specification import SimulationSpecification


def to_urdf(simulation_specification: SimulationSpecification) -> str:
    """
    Converts a simulation specification to URDF.

    :simulation_specification: The simulation specification to convert.
    :returns: The created URDF.
    """
    raise NotImplementedError()
