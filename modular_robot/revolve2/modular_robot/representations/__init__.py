from pathlib import Path

from revolve2.modular_robot import ModularRobot, MorphologicalMeasures

from ._render import Render


def render_robot(robot: ModularRobot, path: Path) -> None:
    body = robot.body
    # if not MorphologicalMeasures(body).is_2d:
    #     raise ValueError("robot is not 2d")

    if path.exists():
        if input(f"Path {path} exists, do you want to overwrite? [y/N] ") == "y":
            path.unlink()
        else:
            raise RuntimeError

    Render().render_robot(body.core, path)
