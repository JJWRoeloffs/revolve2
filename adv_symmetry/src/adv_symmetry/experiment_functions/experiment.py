"""
Different representation testing, generates robot with simple survivor selection (top k% of fittest) with
fixed starting gene length and mutation
Can determine what representation to use with the genotype input parameter to run_experiment
0 == GRN
1 == Tree
2 == CA
"""

import logging
from typing import List, Tuple
from pathlib import Path
import asyncio
import json
import matplotlib.pyplot as plt
import numpy as np

from revolve2.ci_group.logging import setup_logging
from revolve2.modular_robot.brains import BrainCpgNetworkNeighborRandom
from revolve2.modular_robot import (
    ModularRobot,
    get_body_states_single_robot,
    MorphologicalMeasures,
)
from revolve2.experimentation.genotypes.protocols import IGenotype
from revolve2.modular_robot.representations import render_robot
from revolve2.experimentation.genotypes.cellular_automata import (
    CAGenotype,
    CAInitParameters,
)
from revolve2.experimentation.genotypes.tree import (
    TreeGenotype,
    TreeInitParameters,
)
from revolve2.experimentation.genotypes.grn import GRNGenotype, GRNInitParams
from revolve2.ci_group.simulation import create_batch_single_robot_standard
from revolve2.ci_group import terrains, fitness_functions
from revolve2.simulators.mujoco import LocalRunner

# UNDER CONSTRUCTION
def initialize_GRNGenotype(num_individuals: int, rng) -> List[IGenotype]:
    # If you run with a set seed, use the following lines instead.
    # SEED = 1234
    # rng = revolve2.ci_group.rng.make_rng(SEED)

    params = GRNInitParams(max_modules=10)
    return GRNGenotype.random_individuals(params, num_individuals, rng)

def initialize_TreeGenotype(num_individuals: int, rng) -> List[IGenotype]:
    params = TreeInitParameters(max_depth=5)
    return TreeGenotype.random_individuals(params, num_individuals, rng)

def initialize_CAGenotype(num_individuals: int, rng) -> List[IGenotype]:
    # If you run with a set seed, use the following lines instead.
    # SEED = 1234
    # rng = revolve2.ci_group.rng.make_rng(SEED)

    params = CAInitParameters(domain_size=10, iterations=6, nr_rules=10)
    return CAGenotype.random_individuals(params, num_individuals, rng)

def run_generation(previous_population: List[IGenotype], itteration: int, rng, symmetrical : bool = False, weightless : bool = False, terrain : terrains = terrains.flat()):
    """
    Run all runs of an experiment using the provided parameters.

    """
    # Create a list where we will store the success ratio for each repetition.
    generation_fitness = []
    current_population = []

    for itter, individual in enumerate(previous_population):
        if symmetrical:
            g = individual.mutate(rng).as_symmetrical()
        else:
            g = individual.mutate(rng)


        body = g.develop()

        body_measures = MorphologicalMeasures(body=body)

        # We choose a 'CPG' brain with random parameters (the exact working will not be explained here).
        brain = BrainCpgNetworkNeighborRandom(rng)
        # Combine the body and brain into a modular robot.
        robot = ModularRobot(body, brain)
        render_robot(robot, Path() / f"{itteration}_{itter}_robot.png")
        #ADD TERRAINS HERE terrains.slope, terrains.flat
        batch = create_batch_single_robot_standard(robot=robot, terrain=terrain)

        runner = LocalRunner(headless=True, make_it_rain=weightless)

        results = asyncio.run(runner.run_batch(batch))
        environment_results = results.environment_results[0]

        # We have to map the simulation results back to robot body space.
        # This function calculates the state of the robot body at the start and end of the simulation.
        body_state_begin, body_state_end = get_body_states_single_robot(
            body, environment_results
        )

        # Calculate the xy displacement from the body states.
        xy_displacement = fitness_functions.xy_displacement(
            body_state_begin, body_state_end
        )

        generation_fitness.append(xy_displacement)

        #logging xy symmetry
        logging.info(f"xy_symmetry = {body_measures.xy_symmetry}")
        logging.info(f"xz_symmetry = {body_measures.xz_symmetry}")
        logging.info(f"yz_symmetry = {body_measures.yz_symmetry}")

        logging.info(f"xy_displacement = {xy_displacement}")

        current_population.append(g)

    return generation_fitness, current_population

def survivor_selection(generation_fitness, population, percent_survivors):
    # Create a list of (fitness, individual_id) tuples and sort it in descending order
    fitness_with_id = [(fitness, i) for i, fitness in enumerate(generation_fitness)]
    fitness_with_id.sort(reverse=True)

    num_individuals = len(generation_fitness)
    num_survivors = int((percent_survivors / 100) * num_individuals)

    # Select the top N individuals
    top_individuals = [population[i] for _, i in fitness_with_id[:num_survivors]]

    # Determine the number of additional individuals needed to fill the gap
    gap_size = len(population) - len(top_individuals)

    # Insert copies of survived individuals to fill the gap
    for i in range(gap_size):
        top_individuals.append(top_individuals[i % num_survivors])

    return top_individuals

def save_population_to_file(population: List[IGenotype], file_path: Path):
    population_data = [
        {str(k): v for k, v in individual._ca_type.rule_set.items()}
        for individual in population
    ]
    with open(file_path, "w") as f:
        json.dump(population_data, f)


def run_experiment(num_generations: int, 
                   num_individuals: int, 
                   genotype: int = None, 
                   symmetrical : bool = True, 
                   weightless : bool = False, 
                   terrain : terrains = terrains.flat()) -> None:
    """Run the simulation."""
    # Set up standard logging.
    # This decides the level of severity of logged messages we want to display.
    # By default this is 'INFO' or more severe, and 'DEBUG' is excluded.
    # Furthermore, a standard message layout is set up.
    # If logging is not set up, important messages can be missed.
    # We also provide a file name, so the log will be written to both the console and that file.
    setup_logging(file_name="log.txt")
    rng = np.random.default_rng()

    fitness_data = []

    match genotype:
        case 0:
            population = initialize_GRNGenotype(num_individuals, rng)
        case 1:
            population = initialize_TreeGenotype(num_individuals, rng)
        case 2:
            population = initialize_CAGenotype(num_individuals, rng)
        case _:
            population = initialize_TreeGenotype(num_individuals, rng)


    for i, individual in enumerate(population):
        if symmetrical:
            g = individual.mutate(rng).as_symmetrical()
        else:
            g = individual.mutate(rng)
        body = g.develop()
        brain = BrainCpgNetworkNeighborRandom(rng)
        robot = ModularRobot(body, brain)
        try:
            render_robot(robot, Path() / f"{i}_initial.png")
        except IndexError:
            pass

    for i in range(num_generations):
        generation_fitness, population_next = run_generation(population, i, rng, symmetrical, weightless, terrain)
        fitness_data.append([generation_fitness])
        population = survivor_selection(
            generation_fitness.copy(), population_next.copy(), 70
        )

    plt.figure()
    plt.title(f"# generations = {num_generations}, population size = {num_individuals}")
    plt.xlabel("generation")
    plt.ylabel("mean fitness")

    plt.plot(list(range(len(fitness_data))), [np.mean(x) for x in fitness_data])
    plt.savefig(Path() / f"fitness_dynamics_CA_g{num_generations}_p{num_individuals}")

    for i, individual in enumerate(population):
  #      g = individual.mutate(rng)
        body = individual.develop()
        brain = BrainCpgNetworkNeighborRandom(rng)
        robot = ModularRobot(body, brain)

        try:
            render_robot(robot, Path() / f"{i}_final.png")
        except IndexError:
            pass
    # file_path = Path() / "last_population.json"
    # save_population_to_file(population, file_path)

run_experiment(1,2)