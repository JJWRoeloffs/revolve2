"""Batch class."""

from dataclasses import dataclass, field

from ..simulation_specification import SimulationSpecification
from ._batch_parameters import BatchParameters
from ._record_settings import RecordSettings


@dataclass
class Batch:
    """A set of environments and shared parameters for simulation."""

    parameters: BatchParameters

    simulation_specifications: list[SimulationSpecification] = field(
        default_factory=list, init=False
    )
    """The specifications to simulate."""

    record_settings: RecordSettings | None = None
