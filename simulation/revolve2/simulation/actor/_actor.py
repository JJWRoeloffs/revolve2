from dataclasses import dataclass, field
from ..simulation_specification import RigidBody, Joint, SimulationSpecification


@dataclass
class Actor:
    bodies: list[RigidBody] = field(default=list)
    joints: list[Joint] = field(default=list)

    def to_simulation_specification(
        self, simulation_specification: SimulationSpecification, name: str
    ) -> None:
        raise NotImplementedError()
