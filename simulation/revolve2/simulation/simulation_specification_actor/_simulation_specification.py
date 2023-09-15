from ._free_object import FreeObject

from dataclasses import dataclass


@dataclass
class SimulationSpecification:
    free_objects: list[FreeObject]
