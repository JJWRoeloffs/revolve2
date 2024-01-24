from dataclasses import dataclass

from typing import cast, Dict, Any

import marshmallow_dataclass


@dataclass
class Arguments:
    num_generations: int
    num_individuals: int


PARASER = marshmallow_dataclass.class_schema(Arguments)()


def parse_json(json: Dict[str, Any]) -> Arguments:
    return cast(Arguments, PARASER.load(json))
