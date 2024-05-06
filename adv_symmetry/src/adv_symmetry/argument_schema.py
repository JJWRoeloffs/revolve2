from dataclasses import dataclass

from typing import cast, Optional, Dict, Any

import marshmallow_dataclass


@dataclass
class Arguments:
    num_generations: int
    num_individuals: int
    genotype: Optional[int] = None
    symmetrical: bool = True
    weightless: bool = False
    terrain_type: Optional[int] = None
    seed: Optional[int] = None


PARASER = marshmallow_dataclass.class_schema(Arguments)()


def parse_json(json: Dict[str, Any]) -> Arguments:
    return cast(Arguments, PARASER.load(json))
