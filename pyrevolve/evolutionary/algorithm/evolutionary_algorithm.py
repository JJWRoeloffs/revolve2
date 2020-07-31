from typing import List

from pyrevolve.evolutionary import Individual, Fitness
from pyrevolve.evolutionary.agents import Agents
from pyrevolve.evolutionary.algorithm.evolutionary_configurations import EvolutionConfiguration
from pyrevolve.evolutionary.ecology.population import Population
from pyrevolve.evolutionary.algorithm.genome.operators.mutation_operator import MutationOperator
from pyrevolve.evolutionary.algorithm.genome.operators.recombination_operator import RecombinationOperator
from pyrevolve.evolutionary.algorithm.conditions.initialization import Initialization
from pyrevolve.evolutionary.algorithm.selection.selection import ParentSelection, SurvivorSelection
from pyrevolve.evolutionary.algorithm.conditions.special_features import SpecialFeatures
from pyrevolve.evolutionary.algorithm.conditions.termination_condition import TerminationCondition


class EvolutionaryAlgorithm:

    def __init__(self, configuration: EvolutionConfiguration, fitness_type: type(Fitness)):
        self.configuration: EvolutionConfiguration = configuration
        self.fitness_type: type(Fitness) = fitness_type

        self.parent_selection: ParentSelection = self.configuration.parent_selection
        self.survivor_selection: SurvivorSelection = self.configuration.survivor_selection

        self.recombination: RecombinationOperator = self.configuration.recombination
        self.mutation: MutationOperator = self.configuration.mutation

        self.initialization: Initialization = self.configuration.initialization
        self.termination_condition: TerminationCondition = self.configuration.termination_condition
        self.special_features: SpecialFeatures = self.configuration.special_features

    def initialize(self, populations: List[Population]):
        for population in populations:
            for individual in population.individuals:
                individual.representation.init(self.initialization)

    def should_terminate(self, population: Population):
        return self.termination_condition.terminate(population)

    def run(self, population: Population, evaluator):
        parents_list: List[Agents] = self.parent_selection.select(population.individuals)

        offspring: Agents = self._create_offspring(parents_list)

        offspring: Agents = evaluator(offspring)

        population.individuals.extend(offspring)

        population.next_generation(self.survivor_selection.select(population.individuals))

    def _create_offspring(self, parent_list: List[Agents]) -> Agents:
        return Agents(
            [
                Individual(
                    self.mutation.algorithm(
                        self.recombination.algorithm(parents), self.initialization
                    ),
                    self.fitness_type()
                )
                for parents in parent_list
            ]
        )
