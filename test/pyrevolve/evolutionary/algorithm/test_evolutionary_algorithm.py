import unittest

from pyrevolve.evolutionary import Agents, Fitness
from pyrevolve.evolutionary.algorithm.evolutionary_algorithm import EvolutionaryAlgorithm
from pyrevolve.evolutionary.algorithm.evolutionary_configurations import GeneticAlgorithmConfiguration
from pyrevolve.evolutionary.ecology import PopulationEcology
from pyrevolve.evolutionary.ecology.population_management import PopulationManagement
from pyrevolve.evolutionary.individual_factory import IndividualFactory


class TestEvolutionaryAlgorithm(unittest.TestCase):

    def test_initialize(self):

        configuration = GeneticAlgorithmConfiguration()
        evolutionary_algorithm = EvolutionaryAlgorithm(configuration, Fitness)

        population_ecology = PopulationEcology(PopulationManagement())
        population_ecology.initialize(IndividualFactory().create(10))
        evolutionary_algorithm.initialize(population_ecology.populations())

        for population in population_ecology.populations():
            for individual in population.individuals:
                self.assertIsNotNone(individual.representation)

    def test_run(self):

        configuration = GeneticAlgorithmConfiguration()
        evolutionary_algorithm = EvolutionaryAlgorithm(configuration, Fitness)

        population_ecology = PopulationEcology(PopulationManagement())
        population_ecology.initialize(IndividualFactory().create(10))
        evolutionary_algorithm.initialize(population_ecology.populations())

        evolutionary_algorithm.run(population_ecology.populations()[0], evaluator)

        for population in population_ecology.populations():
            for individual in population.individuals:
                self.assertIsNotNone(individual.representation)


def evaluator(offspring: Agents):
    return offspring
