from __future__ import annotations

from dataclasses import dataclass
from revolve2.experimentation.genotypes.protocols import GenotypeInitParams, IGenotype

from typing_extensions import Self

from .develop import Develop
from .genotype import Genotype
from .mutate import mutate_body
from .crossover import crossover_v1
from .random import random_v1

from revolve2.modular_robot import Body
import numpy as np


@dataclass
class GRNInitParams(GenotypeInitParams):
    max_modules: int


class GRNGenotype(IGenotype[GRNInitParams]):
    def __init__(self, params: GRNInitParams, gen: Genotype, seed: int) -> None:
        self.developer = Develop(
            max_modules=params.max_modules, genotype=gen, querying_seed=seed
        )
        self.genotype = gen
        self.params = params

    def as_symmetrical(self) -> Self:
        """Get a version that will develop into a symetrical body"""
        raise NotImplementedError

    def develop(self) -> Body:
        return self.developer.develop()

    def copy(self) -> Self:
        """Get a deeply copied version of the object"""
        raise NotImplementedError

    def mutate(self, rng: np.random.Generator) -> Self:
        """Get a deeply copied version of the object, with some mutation applied"""
        genotype = mutate_body(self.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        genotype = crossover_v1(self.genotype, __o.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    @classmethod
    def random(cls, params: GRNInitParams, rng: np.random.Generator) -> Self:
        """Factory method returning a randomly generated individual"""
        genotype = random_v1(rng)
        return cls._from_genotype(genotype, params, rng)

    @classmethod
    def _from_genotype(
        cls, genotype: Genotype, params: GRNInitParams, rng: np.random.Generator
    ):
        return cls(params, genotype, rng.integers(0, 2**31))
