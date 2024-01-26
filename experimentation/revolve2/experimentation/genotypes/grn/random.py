import numpy as np

from .genotype import Genotype


def random_v1(rng: np.random.Generator) -> Genotype:
    genome_size = 150 + 1
    genotype = [round(rng.uniform(0, 1), 2) for _ in range(genome_size)]
    return Genotype(genotype)
