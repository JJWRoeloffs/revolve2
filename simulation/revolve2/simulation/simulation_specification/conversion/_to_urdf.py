from .._simulation_specification import SimulationSpecification


def to_urdf(
    simulation_specification: SimulationSpecification,
) -> list[tuple[str, bool]]:
    """
    Converts a simulation specification to URDF.

    :simulation_specification: The simulation specification to convert.
    :returns: A urdf string for every disjoint tree, and a flag stating if it's a static object(whether root is fixed).
    """
    return []
