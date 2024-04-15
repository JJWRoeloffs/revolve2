"""
Different representation testing, generates robot with simple survivor selection (top k% of fittest) with
fixed starting gene length and mutation
Can determine what representation to use with the genotype input parameter to run_experiment
0 == GRN
1 == Tree
2 == CA
"""

import json
import logging
from typing import List, Optional, Sequence
from pathlib import Path
import asyncio
import matplotlib.pyplot as plt
import numpy as np

from revolve2.ci_group.logging import setup_logging
from revolve2.modular_robot.brains import BrainCpgNetworkNeighborRandom
from revolve2.modular_robot import (
    ModularRobot,
    get_body_states_single_robot,
)
from revolve2.experimentation.symmetry_measures import (
    calculate_horizontal_symmetry,
    calculate_vertical_symmetry,
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
from revolve2.simulation import Terrain


# UNDER CONSTRUCTION
def initialize_GRNGenotype(
    num_individuals: int, rng: np.random.Generator
) -> Sequence[GRNGenotype]:
    params = GRNInitParams(max_modules=10)
    return GRNGenotype.random_individuals(params, num_individuals, rng)


def initialize_TreeGenotype(
    num_individuals: int, rng: np.random.Generator
) -> Sequence[TreeGenotype]:
    params = TreeInitParameters(max_depth=5)
    return TreeGenotype.random_individuals(params, num_individuals, rng)


def initialize_CAGenotype(
    num_individuals: int, rng: np.random.Generator
) -> Sequence[CAGenotype]:
    params = CAInitParameters(domain_size=10, iterations=6, nr_rules=10)
    return CAGenotype.random_individuals(params, num_individuals, rng)


def run_generation(
    previous_population: Sequence[IGenotype],
    itteration: int,
    rng: np.random.Generator,
    symmetrical: bool = False,
    weightless: bool = False,
    terrain: Terrain = terrains.flat(),
):
    """
    Run all runs of an experiment using the provided parameters.

    """
    # Create a list where we will store the success ratio for each repetition.
    generation_fitness = []
    current_population = []

    for itter, individual in enumerate(previous_population):
        other_parent: IGenotype = rng.choice(np.array(previous_population))
        intermediary = individual.crossover(rng, other_parent)
        if symmetrical:
            g = intermediary.mutate(rng).as_symmetrical()
        else:
            g = intermediary.mutate(rng)

        body = g.develop()
        with (Path() / f"{itter}_{itteration}.json").open("a", encoding="utf-8") as f:
            json.dump(g.to_json(), f)

        # We choose a 'CPG' brain with random parameters (the exact working will not be explained here).
        brain = BrainCpgNetworkNeighborRandom(rng)
        # Combine the body and brain into a modular robot.
        robot = ModularRobot(body, brain)
        # ADD TERRAINS HERE terrains.slope, terrains.flat
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

        vert_symmetry = calculate_vertical_symmetry(body)
        hor_symmetry = calculate_horizontal_symmetry(body)
        # logging xy symmetry
        logging.info(
            f"vert_symmetry = {vert_symmetry}, hor_symmetry = {hor_symmetry} xy_displacement = {xy_displacement}"
        )

        current_population.append(g)

    return generation_fitness, current_population


def survivor_selection(
    generation_fitness, population, percent_survivors
) -> Sequence[IGenotype]:
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


def run_experiment(
    num_generations: int,
    num_individuals: int,
    genotype: Optional[int] = None,
    symmetrical: bool = True,
    weightless: bool = False,
    terrain_type: Optional[int] = None,
    seed: Optional[int] = None,
) -> None:
    """Run the simulation."""
    # Set up standard logging.
    # This decides the level of severity of logged messages we want to display.
    # By default this is 'INFO' or more severe, and 'DEBUG' is excluded.
    # Furthermore, a standard message layout is set up.
    # If logging is not set up, important messages can be missed.
    # We also provide a file name, so the log will be written to both the console and that file.
    setup_logging(file_name="log.txt")
    rng = np.random.default_rng(seed)

    fitness_data = []

    match terrain_type:
        case 0:
            terrain = terrains.flat()
        case 1:
            terrain = terrains.slope()
        case _:
            terrain = terrains.flat()

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
        generation_fitness, population_next = run_generation(
            population, i, rng, symmetrical, weightless, terrain
        )
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


if __name__ == "__main__":
    run_experiment(1, 2, 0)
