from abc import abstractmethod
from typing import cast

import numpy as np
from revolve2.modular_robot import Body, Core
from typing_extensions import Self

from .genotype import GenotypeInitParams, IGenotype
from .nodes import CoreNode, Node, without_overlap


class SymmetricalGenotype(IGenotype):
    def __init__(self, base: IGenotype) -> None:
        self.base = base

    @classmethod
    @abstractmethod
    def wrapped(cls) -> type[IGenotype]:
        ...

    @classmethod
    def random(cls, params: GenotypeInitParams, rng: np.random.Generator) -> Self:
        return cls(cls.wrapped().random(params, rng))

    def develop(self) -> Body:
        nonsymmetric = self.base.develop().core
        body = Body()
        body.core = cast(
            Core,
            without_overlap(
                cast(CoreNode, Node.from_module(nonsymmetric)), max_x=0
            ).to_module_expanded(),
        )
        body.finalize()
        return body

    @classmethod
    def from_params(cls, params: GenotypeInitParams) -> Self:
        return cls(cls.wrapped()(params))

    def copy(self) -> Self:
        return self.__class__(self.base.copy())

    def as_symmetrical(self) -> Self:
        return self.copy()

    def mutate(self, rng: np.random.Generator) -> Self:
        return self.__class__(self.base.mutate(rng))

    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        return self.__class__(self.base.crossover(rng, __o))
