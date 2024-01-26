from __future__ import annotations

from dataclasses import dataclass
from typing import Set, Tuple, List, TypeVar, cast

from numpy.random import Generator
from revolve2.modular_robot import Body, Core, Directions

from revolve2.experimentation.genotypes.protocols import GenotypeInitParams, IGenotype
from revolve2.experimentation.genotypes.tree import (
    Nodes_t,
    Node,
    CoreNode,
    BrickNode,
    ActiveHingeNode,
    RotatedActiveHingeNode,
)

Nodes_gT = TypeVar("Nodes_gT", bound=Nodes_t)
Nodes_g = TypeVar("Nodes_g", bound=Node)

Location = Tuple[int, int]


@dataclass
class TreeInitParameters(GenotypeInitParams):
    max_depth: int


class TreeGenotype(IGenotype[TreeInitParameters]):
    VALID_CHILDREN = [BrickNode, ActiveHingeNode, RotatedActiveHingeNode]

    def __init__(
        self,
        params: TreeInitParameters,
        tree: CoreNode = CoreNode((d, None) for d in CoreNode.valid_attatchments()),
    ) -> None:
        self._params = params
        self._tree: CoreNode = tree
        self._prune_overlap()

    @classmethod
    def _random_subtree(
        cls, node_t: type[Nodes_gT], depth: int, rng: Generator
    ) -> Nodes_gT:
        # Monads hide in little corners. Watch out!
        return node_t(
            (d, cls._random_subtree(childtype, depth - 1, rng))
            for d in node_t.valid_attatchments()
            if depth >= 0
            if (childtype := rng.choice(cls.VALID_CHILDREN + [None])) is not None
        )

    @classmethod
    def random(cls, params: TreeInitParameters, rng: Generator) -> TreeGenotype:
        return cls(params, cls._random_subtree(CoreNode, params.max_depth, rng))

    def develop(self) -> Body:
        assert not self._prune_overlap()
        body = Body()
        body.core = cast(Core, self._tree.to_module())
        body.finalize()
        return body

    def copy(self) -> TreeGenotype:
        return self.__class__(self._params, self._tree.copy())

    def crossover(self, rng: Generator, __o: TreeGenotype) -> TreeGenotype:
        selftree, otree = self._tree.copy(), __o._tree.copy()
        tree = CoreNode(
            (d, selftree.get_child(d))
            if d in rng.choice(Directions.values(), 2)
            else (d, otree.get_child(d))
            for d in CoreNode.valid_attatchments()
        )
        return self.__class__(self._params, tree)

    def mutate(self, rng: Generator) -> TreeGenotype:
        newtree: CoreNode = self._tree.copy()
        node, depth = rng.choice(list(newtree.subnodes()))
        node.set_child(
            self._random_subtree(
                rng.choice(self.VALID_CHILDREN), self._params.max_depth - depth, rng
            ),
            rng.choice(node.valid_attatchments()),
        )
        return self.__class__(self._params, newtree)

    def _prune_overlap(self) -> bool:
        self._occupied_slots: Set[Location] = set()

        # Yes, this can be done with vector algebra,
        # However, counterargument: I am lazy
        def add_angle(location: Location, d: Directions) -> Location:
            x, y = location
            match d:
                case Directions.FRONT:
                    return x, y + 1
                case Directions.BACK:
                    return x, y - 1
                case Directions.RIGHT:
                    return x + 1, y
                case Directions.LEFT:
                    return x - 1, y

        def inner(node: Nodes_g, par_d: Directions, location: Location) -> Nodes_g:
            assert location not in self._occupied_slots
            self._occupied_slots.add(location)
            new_children: List[Tuple[Directions, Node]] = []
            for child_d, child in node.children:
                new_dir = Directions.from_angle(par_d.to_angle() + child_d.to_angle())
                child_loc = add_angle(location, new_dir)
                if child_loc not in self._occupied_slots:
                    new_children.append((child_d, inner(child, new_dir, child_loc)))

            return node.__class__(new_children)

        new_tree = inner(self._tree, Directions.FRONT, (0, 0))
        ret = self._tree != new_tree
        self._tree: CoreNode = new_tree
        del self._occupied_slots

        return ret

    def print_tree(self) -> None:
        def inner(node: Node, type_str: str, depth: int) -> None:
            print(f"{'│   ' * depth}{type_str} - {node.__class__.__name__}")
            for direction, child in node.children:
                inner(child, direction.name, depth + 1)

        inner(self._tree, "HEAD ", 0)
