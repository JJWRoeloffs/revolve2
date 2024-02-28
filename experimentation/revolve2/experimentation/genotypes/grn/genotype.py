from typing import List


class Genotype:
    def __init__(self, genotype: List[float]):
        assert isinstance(genotype, List)
        assert all(isinstance(x, float) for x in genotype)
        self.genotype = genotype
