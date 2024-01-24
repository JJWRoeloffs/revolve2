from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from typing_extensions import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from revolve2.modular_robot import Body
    import numpy as np


class GenotypeInitParams(ABC):
    @abstractmethod
    def __init__(self) -> None:
        ...


InitParams = TypeVar("InitParams", bound=GenotypeInitParams)


class IGenotype(Generic[InitParams], ABC):
    @abstractmethod
    def __init__(self, params: InitParams) -> None:
        ...

    @abstractmethod
    def develop(self) -> Body:
        """Develop the genotype into its phenotype"""

    @abstractmethod
    def copy(self) -> IGenotype:
        """Get a deeply copied version of the object"""

    @abstractmethod
    def mutate(self, rng: np.random.Generator) -> IGenotype:
        """Get a deeply copied version of the object, with some mutation applied"""

    @abstractmethod
    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        """Perform crossover between two individuals. Return a new copy"""

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
