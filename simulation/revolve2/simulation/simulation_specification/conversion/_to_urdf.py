from __future__ import annotations
from .._simulation_specification import SimulationSpecification, RigidBody, Joint
from dataclasses import dataclass, field
from typing import TypeAlias, Iterator


def to_urdf(
    simulation_specification: SimulationSpecification,
) -> list[tuple[str, bool]]:
    """
    Converts a simulation specification to URDF.

    :simulation_specification: The simulation specification to convert.
    :returns: A urdf string for every disjoint tree, and a flag stating if it's a static object(whether root is fixed).
    """
    trees = _to_trees(simulation_specification)
    raise NotImplementedError()


def _to_trees(
    simulation_specification: SimulationSpecification,
) -> list[_Tree]:
    rigid_body_to_graph_mapping = _RigidBodyToGraphAndNodeMap()
    for body in simulation_specification.bodies:
        rigid_body_to_graph_mapping[body] = _Graph([_GraphNode(body)])
    for joint in simulation_specification.joints:
        graph1, node1 = rigid_body_to_graph_mapping[joint.body1]
        graph2, node2 = rigid_body_to_graph_mapping[joint.body2]
        if graph1 is graph2:
            raise ValueError(
                "Simulation specification contains cycles in rigid body and joint definition."
            )
        intersection = graph1.intersection(graph2)
        for node in intersection:
            rigid_body_to_graph_mapping[node.body] = intersection
        node1.neighbors.append((node2, joint))
        node2.neighbors.append((node1, joint))

    rigid_body_to_graph_mapping.values()


@dataclass
class _GraphNode:
    this_i
    body: RigidBody
    neighbors: list[tuple[_GraphNode, Joint]] = field(default_factory=list)


class IdentitySet:
    def __init__(self, iterable=None):
        self.data = {}
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        self.data[id(item)] = item

    def remove(self, item):
        item_id = id(item)
        if item_id in self.data:
            del self.data[item_id]
        else:
            raise KeyError(item)

    def discard(self, item):
        item_id = id(item)
        if item_id in self.data:
            del self.data[item_id]

    def pop(self):
        if len(self.data) == 0:
            raise KeyError("pop from an empty set")
        _, item = self.data.popitem()
        return item

    def clear(self):
        self.data.clear()

    def union(self, *others):
        new_set = IdentitySet(self)
        for other in others:
            for item in other:
                new_set.add(item)
        return new_set

    def intersection(self, *others):
        new_set = IdentitySet()
        for item in self:
            if all(item in other for other in others):
                new_set.add(item)
        return new_set

    def difference(self, *others):
        new_set = IdentitySet(self)
        for other in others:
            for item in other:
                new_set.discard(item)
        return new_set

    def __contains__(self, item):
        return id(item) in self.data

    def __iter__(self):
        return iter(self.data.values())

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "{" + ", ".join(map(str, self.data.values())) + "}"


_Graph: TypeAlias = IdentitySet[_GraphNode]


class _RigidBodyToGraphAndNodeMap:
    _inner_mapping: dict[int, tuple[_Graph, _GraphNode]]
    _id_to_obj: dict[int, RigidBody]

    def __init__(self) -> None:
        self._inner_mapping = {}
        self._id_to_obj = {}

    def __setitem__(
        self, rigid_body: RigidBody, graph_and_node: tuple[_Graph, _GraphNode]
    ) -> None:
        obj_id = id(rigid_body)
        self._inner_mapping[obj_id] = graph_and_node
        self._id_to_obj[obj_id] = rigid_body

    def __getitem__(self, rigid_body: RigidBody) -> tuple[_Graph, _GraphNode]:
        return self._inner_mapping[id(rigid_body)]

    def __delitem__(self, rigid_body: RigidBody) -> None:
        obj_id = id(rigid_body)
        del self._inner_mapping[obj_id]
        del self._id_to_obj[obj_id]

    def __contains__(self, rigid_body: RigidBody) -> bool:
        return id(rigid_body) in self._inner_mapping

    def __len__(self) -> int:
        return len(self._inner_mapping)

    def __iter__(self) -> Iterator[tuple[RigidBody, tuple[_Graph, _GraphNode]]]:
        return ((self._id_to_obj[k], v) for k, v in self._inner_mapping.items())

    def keys(self) -> Iterator[RigidBody]:
        return (self._id_to_obj[k] for k in self._inner_mapping.keys())

    def values(self) -> Iterator[tuple[_Graph, _GraphNode]]:
        return iter(self._inner_mapping.values())

    def items(self) -> Iterator[tuple[RigidBody, tuple[_Graph, _GraphNode]]]:
        return ((self._id_to_obj[k], v) for k, v in self._inner_mapping.items())


@dataclass
class _Tree:
    body: RigidBody
    children: list[tuple[_Tree, Joint]]


def _graph_to_tree(graph: _Graph, root: RigidBody) -> _Tree:
    raise NotImplementedError()
