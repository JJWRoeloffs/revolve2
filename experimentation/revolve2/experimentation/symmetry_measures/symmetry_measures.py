#This is meant for the 2d robot representations that we did

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar,cast
from revolve2.experimentation.genotypes.protocols import IGenotype, to_grid, Node, CoreNode
from revolve2.modular_robot import (
    ActiveHinge,
    Body,
    Brick,
    Core,
    Directions,
    Module,
    RightAngles,
)
from typing_extensions import Self
#
def calculate_vertical_symmetry(body : Body) -> float:
    grid = to_grid(cast(CoreNode, Node.from_module(body.core)))
    width = len(grid[0])
    height = len(grid)
    # [core_position] = [
    #     (x, y)
    #     for x, node in x enumarate(xs)
    #     for y, xs in enumarate(grid)
    #     if isinstance(node, CoreNode)
    # ] find below in readable
    core_position = (0,0)
    number_of_modules = 0
    for i in range(0,height):
        for j in range(0,width):
            if isinstance(grid[i][j],CoreNode):
                core_position = (i,j)
                number_of_modules += 1
            elif grid[i][j] is not None:
                number_of_modules += 1
    print(number_of_modules)
    #Calculate symmetry
    symmetrical_nodes = 0
    for y in range(0,height):
        for x in range(1,(width-1)//2 + 1):
            if core_position[1]-x < 0 or core_position[1] + x >= width:
                pass
            else:
                if grid[y][core_position[1]-x] is not None and type(
                grid[y][core_position[1]-x]) == type(grid[y][core_position[1]+x]):
                    symmetrical_nodes += 2
    #remove modules in axis of core as they dont count for the symmetry measure
        if grid[y][core_position[1]] is not None:
            number_of_modules -= 1    
    if number_of_modules == 0 :
        return 1.0
    print(grid)
    print(symmetrical_nodes)
    print(number_of_modules)
    return symmetrical_nodes/number_of_modules

                    






