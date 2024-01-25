import multineat

from .genotype import Genotype


def mutate_body(
    genotype,
    rng,
) -> Genotype:
    position = rng.sample(range(0, len(genotype.genotype)), 1)[0]
    match rng.sample(["perturbation", "deletion", "addition", "swap"], 1)[0]:
        case "perturbation":
            newv = round(genotype.genotype[position] + rng.normalvariate(0, 0.1), 2)
            if newv > 1:
                genotype.genotype[position] = 1
            elif newv < 0:
                genotype.genotype[position] = 0
            else:
                genotype.genotype[position] = newv

        case "deletion":
            genotype.genotype.pop(position)

        case "addition":
            genotype.genotype.insert(position, round(rng.uniform(0, 1), 2))

        case "swap":
            position2 = rng.sample(range(0, len(genotype.genotype)), 1)[0]
            while position == position2:
                position2 = rng.sample(range(0, len(genotype.genotype)), 1)[0]

            position_v = genotype.genotype[position]
            position2_v = genotype.genotype[position2]
            genotype.genotype[position] = position2_v
            genotype.genotype[position2] = position_v

    return genotype
