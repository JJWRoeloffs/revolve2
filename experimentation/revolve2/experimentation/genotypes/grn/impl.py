from __future__ import annotations

import copy
from dataclasses import dataclass

import numpy as np
from revolve2.experimentation.genotypes.protocols import GenotypeInitParams, IGenotype
from revolve2.experimentation.genotypes.protocols.symmetrical import SymmetricalGenotype
from revolve2.modular_robot import Body

from typing import Dict, Any
from typing_extensions import Self

from .crossover import crossover_v1
from .develop import Develop
from .genotype import Genotype
from .mutate import mutate_body
from .random import random_v1


@dataclass
class GRNInitParams(GenotypeInitParams):
    max_modules: int


class GRNGenotype(IGenotype[GRNInitParams]):
    def __init__(self, params: GRNInitParams, gen: Genotype, seed: int) -> None:
        self.genotype = gen
        self.params = params
        self.seed = seed

    def as_symmetrical(self) -> SymmetricalGRNGenotype:
        """Get a version that will develop into a symetrical body"""
        return SymmetricalGRNGenotype(self)

    def develop(self) -> Body:
        developer = Develop(
            max_modules=self.params.max_modules,
            genotype=self.genotype,
            querying_seed=self.seed,
        )
        return developer.develop()

    def copy(self) -> Self:
        """Get a deeply copied version of the object"""
        return self.__class__(self.params, copy.deepcopy(self.genotype), self.seed)

    def mutate(self, rng: np.random.Generator) -> Self:
        """Get a deeply copied version of the object, with some mutation applied"""
        genotype = mutate_body(self.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    def crossover(self, rng: np.random.Generator, __o: Self) -> Self:
        genotype = crossover_v1(self.genotype, __o.genotype, rng)
        return self._from_genotype(genotype, self.params, rng)

    def to_json(self) -> Dict[str, Any]:
        """Seralise the genotype to Json"""
        return {
            "type": "GRNGenotype",
            "gene": self.genotype.genotype,
            "params": self.params.to_json(),
            "seed": self.seed,
        }

    @classmethod
    def from_json(cls, json_out: Dict[str, Any]) -> Self:
        """Deserialise the genotype from Json"""
        assert json_out["type"] == "GRNGenotype"
        return cls(
            GRNInitParams.from_json(json_out["params"]),
            Genotype(json_out["gene"]),
            json_out["seed"],
        )

    @classmethod
    def random(cls, params: GRNInitParams, rng: np.random.Generator) -> Self:
        """Factory method returning a randomly generated individual"""
        genotype = random_v1(rng)
        return cls._from_genotype(genotype, params, rng)

    @classmethod
    def _from_genotype(
        cls, genotype: Genotype, params: GRNInitParams, rng: np.random.Generator
    ):
        return cls(params, genotype, int(rng.integers(2**31)))


class SymmetricalGRNGenotype(SymmetricalGenotype):
    @classmethod
    def wrapped(cls) -> type[GRNGenotype]:
        return GRNGenotype
