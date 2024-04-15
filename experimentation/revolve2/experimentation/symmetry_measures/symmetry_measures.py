# This is meant for the 2d robot representations that we did

from __future__ import annotations

from typing import cast
from revolve2.experimentation.genotypes.protocols import to_grid, Node, CoreNode
from revolve2.modular_robot import Body


#
def calculate_vertical_symmetry(body: Body) -> float:
    grid = to_grid(cast(CoreNode, Node.from_module(body.core)))
    width = len(grid[0])
    height = len(grid)

    core_position = (0, 0)
    number_of_modules = 0
    for i in range(0, height):
        for j in range(0, width):
            if isinstance(grid[i][j], CoreNode):
                core_position = (i, j)
                number_of_modules += 1
            elif grid[i][j] is not None:
                number_of_modules += 1

    # Calculate symmetry
    symmetrical_nodes = 0
    for y in range(0, height):
        for x in range(1, (width - 1) // 2 + 1):
            if core_position[1] - x < 0 or core_position[1] + x >= width:
                pass
            else:
                if grid[y][core_position[1] - x] is not None and type(
                    grid[y][core_position[1] - x]
                ) == type(grid[y][core_position[1] + x]):
                    symmetrical_nodes += 2
        # remove modules in axis of core as they dont count for the symmetry measure
        if grid[y][core_position[1]] is not None:
            number_of_modules -= 1
    if number_of_modules == 0:
        return 1.0

    return symmetrical_nodes / number_of_modules


def calculate_horizontal_symmetry(body: Body) -> float:
    grid = to_grid(cast(CoreNode, Node.from_module(body.core)))
    width = len(grid[0])
    height = len(grid)

    core_position = (0, 0)
    number_of_modules = 0
    for i in range(0, height):
        for j in range(0, width):
            if isinstance(grid[i][j], CoreNode):
                core_position = (i, j)
                number_of_modules += 1
            elif grid[i][j] is not None:
                number_of_modules += 1
    # Calculate symmetry
    symmetrical_nodes = 0
    for x in range(0, width):
        for y in range(1, (height - 1) // 2 + 1):
            if core_position[0] - y < 0 or core_position[0] + y >= height:
                pass
            else:
                if grid[core_position[0] - y][x] is not None and type(
                    grid[core_position[0] - y][x]
                ) == type(grid[core_position[0] + y][x]):
                    symmetrical_nodes += 2
        # remove modules in axis of core as they dont count for the symmetry measure
        if grid[core_position[0]][x] is not None:
            number_of_modules -= 1
    if number_of_modules == 0:
        return 1.0

    return symmetrical_nodes / number_of_modules
