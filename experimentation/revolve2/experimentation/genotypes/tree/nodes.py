from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Iterable, Optional, List, Tuple, Union
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
        ret = self._association()(angle)
        for d, child in self.children:
            ret.set_child(child.to_module(), d)
        return ret

    def copy(self) -> Self:
        return self.__class__((d, c.copy()) for d, c in self.children)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return all(o == v for o, v in zip(self._children, __value._children))

        return NotImplemented

    @classmethod
    @abstractmethod
    def _association(cls) -> type[Modules_t]:
        ...

    @classmethod
    @abstractmethod
    def valid_attatchments(cls) -> List[Directions]:
        ...


class CoreNode(Node):
    @classmethod
    def _association(cls) -> type[Core]:
        return Core

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT, Directions.LEFT, Directions.RIGHT, Directions.LEFT]


class BrickNode(Node):
    @classmethod
    def _association(cls) -> type[Brick]:
        return Brick

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT, Directions.LEFT, Directions.RIGHT]


class ActiveHingeNode(Node):
    @classmethod
    def _association(cls) -> type[ActiveHinge]:
        return ActiveHinge

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT]


class RotatedActiveHingeNode(Node):
    @classmethod
    def _association(cls) -> type[ActiveHinge]:
        return ActiveHinge

    @classmethod
    def valid_attatchments(cls) -> List[Directions]:
        return [Directions.FRONT]

    def to_module(self, angle: RightAngles = RightAngles.RAD_0) -> Module:
        ret = ActiveHinge(angle + RightAngles.RAD_HALFPI)
        for d, child in self.children:
            ret.set_child(child.to_module(RightAngles.RAD_ONEANDAHALFPI), d)
        return ret


Modules_t = Union[Core, Brick, ActiveHinge]
Nodes_t = Union[CoreNode, BrickNode, ActiveHingeNode, RotatedActiveHingeNode]
