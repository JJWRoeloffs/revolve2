from pathlib import Path

from revolve2.modular_robot import ModularRobot, MorphologicalMeasures

from ._render import Render


def render_robot(robot: ModularRobot, path: Path) -> None:
    Render().render_robot(robot.body.core, path)
