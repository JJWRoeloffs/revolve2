"""
Different representation testing, generates robot with simple survivor selection (top k% of fittest) with
fixed starting gene length and mutation
Can determine what representation to use with the genotype input parameter to run_experiment

Genotypes:
0 == GRN
1 == Tree
2 == CA

Terrains:
0 == Flase
1 == Slope
"""

from dataclasses import dataclass
import json
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple
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
from revolve2.ci_group.simulation import create_batch_multiple_isolated_robots_standard
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


@dataclass
class Result:
    generation: int
    index: int
    fitness: float
    vert_symmetry: float
    hor_symmetry: float
    genotype: IGenotype

    def to_json(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "index": self.index,
            "fitness": self.fitness,
            "vert_symmetry": self.vert_symmetry,
            "hor_symmetry": self.hor_symmetry,
            "genotype": self.genotype.to_json(),
        }


def run_generation(
    previous_population: Sequence[IGenotype],
    itteration: int,
    rng: np.random.Generator,
    symmetrical: bool = False,
    weightless: bool = False,
    terrain: Terrain = terrains.flat(),
    is_slope = False
) -> Tuple[List[float], Sequence[IGenotype]]:
    """
    Run all runs of an experiment using the provided parameters.
    """
    ### SETUP
    current_population: List[IGenotype] = []
    new_robots: List[ModularRobot] = []
    for itter, individual in enumerate(previous_population):
        other_parent: IGenotype = rng.choice(np.array(previous_population))

        g = individual.crossover(rng, other_parent).mutate(rng)
        if symmetrical:
            g = g.as_symmetrical()

        current_population.append(g)
        body = g.develop()
        # We choose a 'CPG' brain with random parameters (the exact working will not be explained here).
        brain = BrainCpgNetworkNeighborRandom(rng)
        # Combine the body and brain into a modular robot.
        new_robots.append(ModularRobot(body, brain))

    ### RUN
    batch = create_batch_multiple_isolated_robots_standard(
        new_robots, [terrain for _ in new_robots]
    )
    runner = LocalRunner(headless=True, make_it_rain=weightless)
    results = asyncio.run(runner.run_batch(batch))

    ### EVAL
    res_file = (
        Path()
        / f"{itteration}_{type(previous_population[0]).__name__}_symmetrical={symmetrical}_water={weightless}_terrain={terrain.name}.jsonl"
    )
    fp = res_file.open("a+", encoding="utf-8")
    generation_fitness = []
    for itter, environment_results in enumerate(results.environment_results):
        # We have to map the simulation results back to robot body space.
        # This function calculates the state of the robot body at the start and end of the simulation.
        body = new_robots[itter].body
        g = current_population[itter]
        body_state_begin, body_state_end = get_body_states_single_robot(
            body, environment_results
        )

        # Calculate the xy displacement from the body states.
        if is_slope:
            xy_displacement = fitness_functions.x_displacement_punish_y_displacement(
                body_state_begin, body_state_end
            )

        else:
            xy_displacement = fitness_functions.xy_displacement(
                body_state_begin, body_state_end
            )
        generation_fitness.append(xy_displacement)

        vert_symmetry = calculate_vertical_symmetry(body)
        hor_symmetry = calculate_horizontal_symmetry(body)
        result = Result(
            generation=itteration,
            index=itter,
            fitness=xy_displacement,
            vert_symmetry=vert_symmetry,
            hor_symmetry=hor_symmetry,
            genotype=g,
        )
        json.dump(result.to_json(), fp)
        fp.write("\n")

    fp.close()

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
            is_slope=False
        case 1:
            terrain = terrains.slope()
            is_slope=True
        case _:
            terrain = terrains.flat()
            is_slope=False
    
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
            res_file = (
                Path()
                /f"{i}_initial_{type(population[i]).__name__}_symmetrical={symmetrical}_water={weightless}_terrain={terrain.name}.png"
            )
            print(res_file)
            render_robot(robot, res_file)
        except IndexError:
            pass

    for i in range(num_generations):
        generation_fitness, population_next = run_generation(
            population, i, rng, symmetrical, weightless, terrain,is_slope
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
    plt.savefig(Path() / f"fitness_dynamics_{type(population[i]).__name__}_symmetrical={symmetrical}_water={weightless}_terrain={terrain.name}_g{num_generations}_p{num_individuals}")

    for i, individual in enumerate(population):
        #      g = individual.mutate(rng)
        body = individual.develop()
        brain = BrainCpgNetworkNeighborRandom(rng)
        robot = ModularRobot(body, brain)

        try:
            res_file = (
                Path()
                / f"{i}_final_{type(population[i]).__name__}_symmetrical={symmetrical}_water={weightless}_terrain={terrain.name}.png"
            )
            render_robot(robot, res_file)
        except IndexError:
            pass
    # file_path = Path() / "last_population.json"
    # save_population_to_file(population, file_path)


if __name__ == "__main__":
    run_experiment(1, 2, 0,terrain_type=1)
