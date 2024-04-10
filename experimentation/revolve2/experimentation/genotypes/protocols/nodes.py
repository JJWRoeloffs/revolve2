from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar

from revolve2.modular_robot import (
    ActiveHinge,
    Brick,
    Core,
    Directions,
    Module,
    RightAngles,
)
from typing_extensions import Self


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
                    child.to_module(RightAngles.RAD_0 - self.base_angle()),
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

    @classmethod
    def from_module(cls, module: Optional[Module]) -> Optional[Self]:
        if module is None:
            return None
        match module:
            case m if isinstance(m, Core):
                node_type = CoreNode
            case m if isinstance(m, Brick):
                node_type = BrickNode
            case m if isinstance(m, ActiveHinge) and m._rotation == 0.0:
                node_type = ActiveHingeNode
            case m if isinstance(m, ActiveHinge):
                node_type = RotatedActiveHingeNode
            case _:
                raise NotImplementedError
        return node_type(
            [
                (Directions(d), cls.from_module(child))
                for d, child in enumerate(module._children)
            ]
        )

    def copy(self) -> Self:
        return self.__class__((d, c.copy()) for d, c in self.children)

    def to_json(self) -> Dict[str, Any]:
        ret = {str(int(d)): c.to_json() for d, c in self.children}
        ret["type"] = self.__class__.__name__
        return ret

    @classmethod
    def from_json(cls, json_out: Dict[str, Any]) -> Self:
        """Inverse of to_json. Hardcodes all implementations of this base class"""
        node_type = json_out.pop("type")
        match node_type:
            case "CoreNode":
                node = CoreNode
            case "BrickNode":
                node = BrickNode
            case "ActiveHingeNode":
                node = ActiveHingeNode
            case "RotatedActiveHingeNode":
                node = RotatedActiveHingeNode
            case other:
                raise ValueError(f"{other} is not a valid node type")
        return node(
            (Directions(int(d)), Node.from_json(c)) for d, c in json_out.items()
        )

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
        return [Directions.FRONT, Directions.LEFT, Directions.RIGHT, Directions.BACK]

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
NODES = [CoreNode, BrickNode, ActiveHingeNode, RotatedActiveHingeNode]


def _add_angle(location: Location, d: Directions) -> Location:
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


def without_overlap(
    tree: Node_T, max_x: int = 10, min_x: int = -10, max_y: int = 10, min_y: int = -10
) -> Node_T:
    _occupied_slots: Set[Location] = set()

    def inner(node: Node_T, par_d: Directions, location: Location) -> Node_T:
        assert location not in _occupied_slots
        _occupied_slots.add(location)
        new_children: List[Tuple[Directions, Node]] = []
        for child_d, child in node.children:
            new_dir = Directions.from_angle(par_d.to_angle() + child_d.to_angle())
            child_loc = _add_angle(location, new_dir)
            if not (min_x <= child_loc[0] <= max_x):
                continue
            if not (min_y <= child_loc[1] <= max_y):
                continue
            if child_loc in _occupied_slots:
                continue
            new_children.append((child_d, inner(child, new_dir, child_loc)))

        return node.__class__(new_children)

    return inner(tree, Directions.FRONT, (0, 0))


def to_grid(tree: Node_T) -> List[List[Optional[Node_T]]]:
    def inner(
        node: Node_T, par_d: Directions, location: Location
    ) -> Iterator[Tuple[Location, Node_T]]:
        yield (location, node)
        for child_d, child in node.children:
            new_dir = Directions.from_angle(par_d.to_angle() + child_d.to_angle())
            child_loc = _add_angle(location, new_dir)
            yield from inner(child, new_dir, child_loc)

    locs = {k: v for k, v in inner(tree, Directions.FRONT, (0, 0))}
    return [
        [
            locs.get((x, y), None)
            for x in range(min(x[0] for x in locs), max(x[0] for x in locs) + 1)
        ]
        for y in range(min(x[1] for x in locs), max(x[1] for x in locs) + 1)
    ]


def print_tree(tree: Node) -> None:
    def inner(node: Node, type_str: str, depth: int) -> None:
        print(f"{'│   ' * depth}{type_str} - {node.__class__.__name__}")
        for direction, child in node.children:
            inner(child, direction.name, depth + 1)

    inner(tree, "HEAD ", 0)