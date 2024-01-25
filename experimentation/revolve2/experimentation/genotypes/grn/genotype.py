from __future__ import annotations

from dataclasses import dataclass

import multineat


@dataclass
class Genotype:
    genotype: multineat.Genome
