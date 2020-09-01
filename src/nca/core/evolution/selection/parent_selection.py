import random
from typing import List

import numpy as np

from nca.core.actor.individual import Individual
from nca.core.evolution.selection.selection import ParentSelection


class RandomParentSelection(ParentSelection):

    def __init__(self):
        super().__init__()

    def algorithm(self, individuals: List[Individual]) -> List[Individual]:
        return random.choices(individuals, k=self.configuration.number_of_parents)


class TournamentSelection(ParentSelection):

    def __init__(self):
        super().__init__()

    def algorithm(self, individuals: List[Individual]) -> List[Individual]:
        return [max(np.random.choice(individuals, self.configuration.tournament_size),
                    key=lambda x: x.fitness)
                for _ in range(self.configuration.number_of_parents)]


class RouletteWheelSelection(ParentSelection):

    def algorithm(self, individuals: List[Individual]) -> List[Individual]:
        return random.choices(individuals,
                              k=self.configuration.number_of_parents,
                              weights=[agent.fitness for agent in individuals])


class NullParentSelection(RandomParentSelection):
    pass
