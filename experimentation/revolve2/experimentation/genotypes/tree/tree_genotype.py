from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, TypeVar, cast

from numpy.random import Generator
from revolve2.experimentation.genotypes.protocols import (
    ActiveHingeNode,
    BrickNode,
    CoreNode,
    GenotypeInitParams,
    IGenotype,
    Node,
    RotatedActiveHingeNode,
    SymmetricalGenotype,
    without_overlap,
)
from revolve2.modular_robot import Body, Core, Directions
from typing_extensions import Self

Node_T = TypeVar("Node_T", bound=Node)


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
        self._tree = without_overlap(tree)

    @classmethod
    def _random_subtree(
        cls, node_t: type[Node_T], depth: int, rng: Generator
    ) -> Node_T:
        # Monads hide in little corners. Watch out!
        return node_t(
            (d, cls._random_subtree(childtype, depth - 1, rng))
            for d in node_t.valid_attatchments()
            if depth >= 0
            if (childtype := rng.choice(cls.VALID_CHILDREN + [None])) is not None
        )

    @classmethod
    def random(cls, params: TreeInitParameters, rng: Generator) -> Self:
        return cls(params, cls._random_subtree(CoreNode, params.max_depth, rng))

    def as_symmetrical(self) -> SymmetricalTreeGenotype:
        return SymmetricalTreeGenotype(self)

    def develop(self) -> Body:
        body = Body()
        body.core = cast(Core, self._tree.to_module())
        body.finalize()
        return body

    def copy(self) -> Self:
        return self.__class__(self._params, self._tree.copy())

    def crossover(self, rng: Generator, __o: Self) -> Self:
        selftree, otree = self._tree.copy(), __o._tree.copy()
        tree = CoreNode(
            (d, selftree.get_child(d))
            if d in rng.choice(Directions.values(), 2)
            else (d, otree.get_child(d))
            for d in CoreNode.valid_attatchments()
        )
        return self.__class__(self._params, tree)

    def mutate(self, rng: Generator) -> Self:
        newtree: CoreNode = self._tree.copy()
        node, depth = rng.choice(list(newtree.subnodes()))
        node.set_child(
            self._random_subtree(
                rng.choice(self.VALID_CHILDREN), self._params.max_depth - depth, rng
            ),
            rng.choice(node.valid_attatchments()),
        )
        return self.__class__(self._params, newtree)

    def to_json(self) -> Dict[str, Any]:
        """Seralise the genotype to Json"""
        return {
            "type": "TreeGenotype",
            "gene": self._tree.to_json(),
            "params": self._params.to_json(),
        }

    @classmethod
    def from_json(cls, json_out: Dict[str, Any]) -> Self:
        """Deserialise the genotype from Json"""
        assert json_out["type"] == "TreeGenotype"
        params = TreeInitParameters.from_json(json_out["params"])
        tree = CoreNode.from_json(json_out["gene"])
        return cls(params, tree)


class SymmetricalTreeGenotype(SymmetricalGenotype):
    @classmethod
    def wrapped(cls) -> type[TreeGenotype]:
        return TreeGenotype