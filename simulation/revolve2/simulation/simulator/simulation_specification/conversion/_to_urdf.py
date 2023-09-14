from .._simulation_specification import SimulationSpecification


def to_urdf(simspec: SimulationSpecification) -> str:
    """
    Converts a simulation specification to URDF.

    :simspec: The simulation specification to convert.
    :returns: The created URDF.
    """
    raise NotImplementedError()
