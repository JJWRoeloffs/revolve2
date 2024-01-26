from __future__ import annotations

from dataclasses import dataclass

from typing import List


@dataclass
class Genotype:
    genotype: List[float]
