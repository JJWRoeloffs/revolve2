from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Iterable, Optional, List, Tuple, Set, TypeVar
from typing_extensions import Self

from revolve2.modular_robot import (
    Directions,
    Module,
    Core,
    Brick,
    ActiveHinge,
    RightAngles,
)


class Node(ABC):
    def __init__(self, children: Iterable[Tuple[Directions, Optional[Node]]]) -> None:
        self._children: List[Optional[Node]] = [None] * len(self.valid_attatchments())
        for direction, child in children:
            if child is not None:
                self.set_child(child, direction)

    def get_child(self, which: Directions) -> Optional[Node]:
        if not which in self.valid_attatchments():
            raise ValueError(f"{which} is no direction of {self.__class__}")
        return self._children[which]

    def set_child(self, item: Node, which: Directions) -> None:
        if not which in self.valid_attatchments():
            raise ValueError(f"{which} is no direction of {self.__class__}")
        self._children[which] = item

    @property
    def children(self) -> List[Tuple[Directions, Node]]:
        return [
            (Directions(direction), child)
            for direction, child in enumerate(self._children)
            if child is not None
        ]

    def subnodes(self) -> Iterable[Tuple[Node, int]]:
        def inner(node: Node, depth: int) -> Iterable[Tuple[Node, int]]:
            yield node, depth
            for _, child in node.children:
                yield from inner(child, depth + 1)

        return inner(self, 0)

    def to_module(self, angle: RightAngles = RightAngles.RAD_0) -> Module:
        ret = self._association()(angle + self.base_angle())
        for d, child in self.children:
            ret.set_child(child.to_module(RightAngles.RAD_0 - self.base_angle()), d)
        return ret

    def to_module_flipped(self, angle: RightAngles = RightAngles.RAD_0) -> Module:
        ret = self._association()(angle + self.base_angle())
        for d, child in self.children:
            ret.set_child(
                child.to_module_flipped(RightAngles.RAD_0 - self.base_angle()),
                d.mirrored(),
            )
        return ret

    def to_module_expanded(self, angle: RightAngles = RightAngles.RAD_0) -> Module:
        ret = self._association()(angle + self.base_angle())
        for d, child in self.children:
            if d == Directions.RIGHT or d == Directions.LEFT:
                ret.set_child(
                    child.to_module_flipped(RightAngles.RAD_0 - self.base_angle()),
                    Directions.RIGHT,
                )
                ret.set_child(
                    child.to_module_flipped(RightAngles.RAD_0 - self.base_angle()),
                    Directions.LEFT,
                )
            else:
                ret.set_child(
                    child.to_module_expanded(RightAngles.RAD_0 - self.base_angle()), d
                )
        return ret

    def copy(self) -> Self:
        return self.__class__((d, c.copy()) for d, c in self.children)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return all(o == v for o, v in zip(self._children, __value._children))

        return NotImplemented

    @classmethod
    @abstractmethod
    def _association(cls) -> type[Module]:
        ...

    @classmethod
    @abstractmethod
    def valid_attatchments(cls) -> List[Directions]:
        ...

    @classmethod
    @abstractmethod
    def base_angle(cls) -> RightAngles:
        ...


Node_T = TypeVar("Node_T", bound=Node)


class CoreNode(Node):
    @classmethod
    def _association(cls) -> type[Core]:
        return Core

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT, Directions.LEFT, Directions.RIGHT, Directions.LEFT]

    @classmethod
    def base_angle(cls) -> RightAngles:
        return RightAngles.RAD_0


class BrickNode(Node):
    @classmethod
    def _association(cls) -> type[Brick]:
        return Brick

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT, Directions.LEFT, Directions.RIGHT]

    @classmethod
    def base_angle(cls) -> RightAngles:
        return RightAngles.RAD_0


class ActiveHingeNode(Node):
    @classmethod
    def _association(cls) -> type[ActiveHinge]:
        return ActiveHinge

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT]

    @classmethod
    def base_angle(cls) -> RightAngles:
        return RightAngles.RAD_0


class RotatedActiveHingeNode(Node):
    @classmethod
    def _association(cls) -> type[ActiveHinge]:
        return ActiveHinge

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT]

    @classmethod
    def base_angle(cls) -> RightAngles:
        return RightAngles.RAD_HALFPI


Location = Tuple[int, int]


def without_overlap(
    tree: Node_T, max_x: int = 10, min_x: int = -10, max_y: int = 10, min_y: int = -10
) -> Node_T:
    _occupied_slots: Set[Location] = set()

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

    def inner(node: Node_T, par_d: Directions, location: Location) -> Node_T:
        assert location not in _occupied_slots
        _occupied_slots.add(location)
        new_children: List[Tuple[Directions, Node]] = []
        for child_d, child in node.children:
            new_dir = Directions.from_angle(par_d.to_angle() + child_d.to_angle())
            child_loc = add_angle(location, new_dir)
            if not (min_x < child_loc[0] < max_x):
                continue
            if not (min_y < child_loc[1] < max_y):
                continue
            if child_loc in _occupied_slots:
                continue
            new_children.append((child_d, inner(child, new_dir, child_loc)))

        return node.__class__(new_children)

    return inner(tree, Directions.FRONT, (0, 0))


def print_tree(tree: Node) -> None:
    def inner(node: Node, type_str: str, depth: int) -> None:
        print(f"{'│   ' * depth}{type_str} - {node.__class__.__name__}")
        for direction, child in node.children:
            inner(child, direction.name, depth + 1)

    inner(tree, "HEAD ", 0)
