from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from typing_extensions import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import numpy as np
    from revolve2.modular_robot import Body


class GenotypeInitParams(ABC):
    @abstractmethod
    def __init__(self) -> None:
        ...

    def to_json(self) -> Dict[str, Any]:
        """Return the Json of the params"""
        return self.__dict__

    @classmethod
    def from_json(cls, json_out: Dict[str, Any]) -> Self:
        return cls(**json_out)


InitParams = TypeVar("InitParams", bound=GenotypeInitParams)


class IGenotype(Generic[InitParams], ABC):
    @abstractmethod
    def __init__(self, params: InitParams) -> None:
        ...

    @abstractmethod
    def as_symmetrical(self) -> IGenotype:
        """Get a version that will develop into a symetrical body"""

    @abstractmethod
    def develop(self) -> Body:
        """Develop the genotype into its phenotype"""

    @abstractmethod
    def copy(self) -> Self:
        """Get a deeply copied version of the object"""

    @abstractmethod
    def mutate(self, rng: np.random.Generator) -> Self:
        """Get a deeply copied version of the object, with some mutation applied"""

    @abstractmethod
    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        """Perform crossover between two individuals. Return a new copy"""

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """Seralise the genotype to Json"""

    @classmethod
    @abstractmethod
    def from_json(cls, json_out: Dict[str, Any]) -> Self:
        """Deserialise the genotype from Json"""

    @classmethod
    @abstractmethod
    def random(cls, params: InitParams, rng: np.random.Generator) -> Self:
        """Factory method returning a randomly generated individual"""

    @classmethod
    def random_individuals(
        cls, params: InitParams, n: int, rng: np.random.Generator
    ) -> List[Self]:
        """Factory method returning randomly generated individuals"""
        return [cls.random(params, rng) for _ in range(n)]
