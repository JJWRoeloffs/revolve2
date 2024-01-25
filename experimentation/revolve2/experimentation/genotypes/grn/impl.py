from __future__ import annotations

from dataclasses import dataclass
import multineat
from revolve2.experimentation.genotypes.protocols import GenotypeInitParams, IGenotype

from typing_extensions import TYPE_CHECKING, Self

from .develop import Develop
from .genotype import Genotype
from .mutate import mutate_body
from .crossover import crossover_v1
from .random import random_v1
from .multineat_parameters import _MULTINEAT_PARAMS

from revolve2.modular_robot import Body
import numpy as np


@dataclass
class GRNInitParams(GenotypeInitParams):
    max_modules: int


class GRNGenotype(IGenotype):
    def __init__(self, params: GRNInitParams, gen: Genotype, seed: int) -> None:
        self.developer = Develop(
            max_modules=params.max_modules, genotype=gen, querying_seed=seed
        )
        self.genotype = gen
        self.params = params

    def develop(self) -> Body:
        return self.developer.develop()

    def copy(self) -> GRNGenotype:
        """Get a deeply copied version of the object"""
        raise NotImplementedError

    def mutate(self, rng: np.random.Generator) -> GRNGenotype:
        """Get a deeply copied version of the object, with some mutation applied"""
        genotype = mutate_body(self.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        genotype = crossover_v1(self.genotype, __o.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    @classmethod
    def random(cls, params: GRNInitParams, rng: np.random.Generator) -> Self:
        """Factory method returning a randomly generated individual"""
        innov_db = multineat.InnovationDatabase()
        num_initial_mutations = 10
        genotype = random_v1(
            innov_db,
            cls._multineat_rng_from_random(rng),
            _MULTINEAT_PARAMS,
            multineat.ActivationFunction.TANH,  # hidden activation type
            7,  # bias(always 1), x1, y1, z1, x2, y2, z2
            1,  # weight
            num_initial_mutations,
        )
        return cls._from_genotype(genotype, params, rng)

    @classmethod
    def _from_genotype(
        cls, genotype: Genotype, params: GRNInitParams, rng: np.random.Generator
    ):
        return cls(params, genotype, int(100 * rng.random()))

    @staticmethod
    def _multineat_rng_from_random(rng: np.random.Generator) -> multineat.RNG:
        """
        Create a multineat rng object from a numpy rng state.

        :param rng: The numpy rng.
        :returns: The multineat rng.
        """
        multineat_rng = multineat.RNG()
        multineat_rng.Seed(rng.integers(0, 2**31))
        return multineat_rng
