from typing import List


class Genotype:
    def __init__(self, genotype: List[float]):
        self.genotype = [float(x) for x in genotype]
