import math
import random
from typing import List, Optional, Tuple, Union

import numpy as np
from revolve2.modular_robot import ActiveHinge, Body, Brick, Core, Directions, Module

from .genotype import Genotype


def random_v1(rng) -> Genotype:
    genome_size = 150 + 1
    genotype = [round(rng.uniform(0, 1), 2) for _ in range(genome_size)]
    return Genotype(genotype)


class Cell:
    def __init__(self) -> None:
        self.developed_module: Optional[Module] = None
        self.transcription_factors = {}


class Develop:
    # develops a Gene Regulatory network
    def __init__(
        self,
        max_modules: int,
        genotype: Genotype,
        querying_seed: int,
    ):
        self.max_modules = max_modules
        self.genotype = genotype.genotype
        self.querying_seed = querying_seed
        self.random = None
        self.cells = []
        self.queried_substrate = {}
        self.phenotype_body = None
        self.quantity_modules = 0

        self.regulatory_transcription_factor_idx = 0
        self.regulatory_min_idx = 1
        self.regulatory_max_idx = 2
        self.transcription_factor_idx = 3
        self.transcription_factor_amount_idx = 4
        self.diffusion_site_idx = 5
        self.types_nucleotypes = 6
        self.diffusion_sites_qt = 4

        self.promoter_threshold = 0.8
        self.concentration_decay = 0.005
        self.structural_trs = len(["brick", "joint", "rotation"])
        # when increasing number of regulatory tfs, genotype size should also increase
        self.regulatory_tfs = 2
        self.increase_scaling = 100
        self.intra_diffusion_rate = self.concentration_decay / 2
        self.inter_diffusion_rate = self.intra_diffusion_rate / 8
        self.dev_steps = 100
        self.concentration_threshold = self.genotype[0]
        self.genotype = self.genotype[1:]

    def develop(self) -> Body:
        self.random = random.Random(self.querying_seed)
        self.quantity_nodes = 0
        self.phenotype_body = self.develop_body()
        self.phenotype_body.finalize()

        return self.phenotype_body

    def develop_body(self) -> Body:
        self.gene_parser()
        self.regulate()

        if self.phenotype_body is None:
            raise ValueError("Cannot return non-developed body")

        return self.phenotype_body

    # parses genotype to discover promotor sites and compose genes
    def gene_parser(self):
        promotors = []
        nucleotide_idx = 0
        while nucleotide_idx < len(self.genotype):
            if self.genotype[nucleotide_idx] < self.promoter_threshold:
                # if there are nucleotypes enough to compose a gene
                if (len(self.genotype) - 1 - nucleotide_idx) >= self.types_nucleotypes:
                    regulatory_transcription_factor = self.genotype[
                        nucleotide_idx + self.regulatory_transcription_factor_idx + 1
                    ]  # gene product
                    regulatory_min = self.genotype[
                        nucleotide_idx + self.regulatory_min_idx + 1
                    ]
                    regulatory_max = self.genotype[
                        nucleotide_idx + self.regulatory_max_idx + 1
                    ]
                    transcription_factor = self.genotype[
                        nucleotide_idx + self.transcription_factor_idx + 1
                    ]
                    transcription_factor_amount = self.genotype[
                        nucleotide_idx + self.transcription_factor_amount_idx + 1
                    ]
                    diffusion_site = self.genotype[
                        nucleotide_idx + self.diffusion_site_idx + 1
                    ]
                    # print(nucleotide_idx)
                    # print(regulatory_transcription_factor,regulatory_min,regulatory_max,transcription_factor,transcription_factor_amount,diffusion_site)
                    # begin: converts tfs values into labels #
                    range_size = 1 / (self.structural_trs + self.regulatory_tfs)
                    limits = [
                        round(limit / 100, 2)
                        for limit in range(0, 1 * 100, int(range_size * 100))
                    ]
                    regulatory_transcription_factor_label = None
                    transcription_factor_label = None

                    for idx in range(0, len(limits) - 1):
                        if (
                            regulatory_transcription_factor >= limits[idx]
                            and regulatory_transcription_factor < limits[idx + 1]
                        ):
                            regulatory_transcription_factor_label = "TF" + str(
                                len(limits)
                            )

                        if (
                            transcription_factor >= limits[idx]
                            and transcription_factor < limits[idx + 1]
                        ):
                            transcription_factor_label = "TF" + str(idx + 1)
                        elif transcription_factor >= limits[idx + 1]:
                            transcription_factor_label = "TF" + str(len(limits))

                    # if regulatory_transcription_factor_label is None:
                    #     raise ValueError("cannot parse gene without length")
                    # if transcription_factor_label is None:
                    #     raise ValueError("cannot parse gene without length")

                    # ends: converts tfs values into labels #

                    # begin: converts diffusion sites values into labels #
                    range_size = 1 / self.diffusion_sites_qt
                    limits = [
                        round(limit / 100, 2)
                        for limit in range(0, 1 * 100, int(range_size * 100))
                    ]
                    diffusion_site_label = None
                    for idx in range(0, len(limits) - 1):
                        if limits[idx + 1] > diffusion_site >= limits[idx]:
                            diffusion_site_label = idx
                        elif diffusion_site >= limits[idx + 1]:
                            diffusion_site_label = len(limits) - 1
                    # if diffusion_site_label is None:
                    #     raise ValueError("cannot parse gene without length")

                    gene = [
                        regulatory_transcription_factor_label,
                        regulatory_min,
                        regulatory_max,
                        transcription_factor_label,
                        transcription_factor_amount,
                        diffusion_site_label,
                    ]

                    promotors.append(gene)

                    nucleotide_idx += self.types_nucleotypes
            nucleotide_idx += 1
        self.promotors = np.array(promotors)
        # pprint.pprint(self.promotors)

    def regulate(self):
        self.maternal_injection()
        self.growth()

    def growth(self):
        # print('\ngrowth')
        for t in range(0, self.dev_steps):
            # print('\n> ----t ',t, '\n')
            # develops cells in order of age
            for idxc in range(0, len(self.cells)):
                # print(' \n ---cell ', idxc, '\n')
                cell = self.cells[idxc]
                for tf in cell.transcription_factors:
                    # print(' ', tf)
                    self.increase(tf, cell)
                    self.intra_diffusion(tf, cell)
                    self.inter_diffusion(tf, cell)
                #    print(tf, [ '%.4f' % elem for elem in cell.transcription_factors[tf]], round(sum(cell.transcription_factors[tf]),2))

                # print('\n place module')
                self.place_module(cell)

                # print('decay')
                for tf in cell.transcription_factors:
                    self.decay(tf, cell)

    def increase(self, tf: int, cell: Cell):
        # increase concentration in due diffusion sites
        tf_promotors = np.where(self.promotors[:, self.transcription_factor_idx] == tf)[
            0
        ]
        for tf_promotor_idx in tf_promotors:
            cell.transcription_factors[tf][
                int(self.promotors[tf_promotor_idx][self.diffusion_site_idx])
            ] += float(
                self.promotors[tf_promotor_idx][self.transcription_factor_amount_idx]
            ) / float(
                self.increase_scaling
            )

    def inter_diffusion(self, tf: int, cell: Cell):
        for ds in range(0, self.diffusion_sites_qt):
            # back slot of all modules but core send to a parent
            if ds == Core.BACK and (
                type(cell.developed_module) == ActiveHinge
                or type(cell.developed_module) == Brick
            ):
                if (
                    cell.transcription_factors[tf][Core.BACK]
                    >= self.inter_diffusion_rate
                ):
                    cell.transcription_factors[tf][
                        Core.BACK
                    ] -= self.inter_diffusion_rate

                    # updates or includes
                    if cell.developed_module._parent.cell.transcription_factors.get(tf):
                        cell.developed_module._parent.cell.transcription_factors[tf][
                            cell.developed_module.direction_from_parent
                        ] += self.inter_diffusion_rate
                    else:
                        cell.developed_module._parent.cell.transcription_factors[tf] = [
                            0
                        ] * self.diffusion_sites_qt
                        cell.developed_module._parent.cell.transcription_factors[tf][
                            cell.developed_module.direction_from_parent
                        ] += self.inter_diffusion_rate

            # in the case of joint, shares also concentrations of sites without slot
            elif type(cell.developed_module) == ActiveHinge and ds in [
                Core.LEFT,
                Core.FRONT,
                Core.RIGHT,
            ]:
                if (
                    cell.developed_module.children[Core.FRONT] is not None
                    and cell.transcription_factors[tf][ds] >= self.inter_diffusion_rate
                ):
                    cell.transcription_factors[tf][ds] -= self.inter_diffusion_rate

                    # updates or includes
                    if cell.developed_module.children[
                        Core.FRONT
                    ].cell.transcription_factors.get(tf):
                        cell.developed_module.children[
                            Core.FRONT
                        ].cell.transcription_factors[tf][
                            Core.BACK
                        ] += self.inter_diffusion_rate
                    else:
                        cell.developed_module.children[
                            Core.FRONT
                        ].cell.transcription_factors[tf] = [0] * self.diffusion_sites_qt
                        cell.developed_module.children[
                            Core.FRONT
                        ].cell.transcription_factors[tf][
                            Core.BACK
                        ] += self.inter_diffusion_rate
            else:
                if (
                    cell.developed_module.children[ds] is not None
                    and cell.transcription_factors[tf][ds] >= self.inter_diffusion_rate
                ):
                    cell.transcription_factors[tf][ds] -= self.inter_diffusion_rate

                    # updates or includes
                    if cell.developed_module.children[
                        ds
                    ].cell.transcription_factors.get(tf):
                        cell.developed_module.children[ds].cell.transcription_factors[
                            tf
                        ][Core.BACK] += self.inter_diffusion_rate
                    else:
                        cell.developed_module.children[ds].cell.transcription_factors[
                            tf
                        ] = [0] * self.diffusion_sites_qt
                        cell.developed_module.children[ds].cell.transcription_factors[
                            tf
                        ][Core.BACK] += self.inter_diffusion_rate

    def intra_diffusion(self, tf: int, cell: Cell):
        # for each site: first right then left
        for ds in range(0, self.diffusion_sites_qt):
            # print(' ds', ds)
            ds_left = ds - 1 if ds - 1 >= 0 else self.diffusion_sites_qt - 1
            ds_right = ds + 1 if ds + 1 <= self.diffusion_sites_qt - 1 else 0

            if cell.transcription_factors[tf][ds] >= self.intra_diffusion_rate:
                cell.transcription_factors[tf][ds] -= self.intra_diffusion_rate
                cell.transcription_factors[tf][ds_right] += self.intra_diffusion_rate

            if cell.transcription_factors[tf][ds] >= self.intra_diffusion_rate:
                cell.transcription_factors[tf][ds] -= self.intra_diffusion_rate
                cell.transcription_factors[tf][ds_left] += self.intra_diffusion_rate

    def decay(self, tf: int, cell: Cell):
        # decay in all sites
        for ds in range(0, self.diffusion_sites_qt):
            cell.transcription_factors[tf][ds] = max(
                0, cell.transcription_factors[tf][ds] - self.concentration_decay
            )

    def place_module(self, cell: Cell):
        tds_qt = self.structural_trs + self.regulatory_tfs
        product_tfs = []
        modules_types = [Brick, ActiveHinge]
        for tf in range(tds_qt - len(modules_types) - 1, tds_qt):
            product_tfs.append(f"TF{tf+1}")
        #  print(product_tfs)
        concentration1 = (
            sum(cell.transcription_factors[product_tfs[0]])
            if cell.transcription_factors.get(product_tfs[0])
            else 0
        )  # B

        concentration2 = (
            sum(cell.transcription_factors[product_tfs[1]])
            if cell.transcription_factors.get(product_tfs[1])
            else 0
        )  # A

        concentration3 = (
            sum(cell.transcription_factors[product_tfs[2]])
            if cell.transcription_factors.get(product_tfs[2])
            else 0
        )  # rotation
        #  print('conc rot', concentration3)
        # chooses tf with the highest concentration
        product_concentrations = [concentration1, concentration2]
        idx_max = product_concentrations.index(max(product_concentrations))

        # print('concent prod', [ '%.4f' % elem for elem in product_concentrations])
        # if tf concentration above a threshold
        if product_concentrations[idx_max] > self.concentration_threshold:
            # grows in the free diffusion site with the highest concentration
            freeslots = np.array([c is None for c in cell.developed_module.children])
            if type(cell.developed_module) == Brick:
                freeslots = np.append(freeslots, [False])  # brick has no back
            elif type(cell.developed_module) == ActiveHinge:
                freeslots = np.append(
                    freeslots, [False, False, False]
                )  # joint has no back nor left or right

            #   print('free in highest',freeslots )
            if any(freeslots):  # TODO: check also if substrate free
                true_indices = np.where(freeslots)[0]
                values_at_true_indices = np.array(
                    cell.transcription_factors[product_tfs[idx_max]]
                )[true_indices]
                max_value_index = np.argmax(values_at_true_indices)
                position_of_max_value = true_indices[max_value_index]
                slot = position_of_max_value

                potential_module_coord, turtle_direction = self.calculate_coordinates(
                    cell.developed_module, slot
                )
                if (
                    potential_module_coord not in self.queried_substrate.keys()
                    and self.quantity_modules < self.max_modules - 1
                ):
                    module_type = modules_types[idx_max]

                    # rotates only joints and if defined by concentration
                    orientation = (
                        1 if concentration3 > 0.5 and module_type == ActiveHinge else 0
                    )
                    absolute_rotation = 0
                    if module_type == ActiveHinge and orientation == 1:
                        if (
                            type(cell.developed_module) == ActiveHinge
                            and cell.developed_module._absolute_rotation == 1
                        ):
                            absolute_rotation = 0
                        else:
                            absolute_rotation = 1
                    else:
                        if (
                            type(cell.developed_module) == ActiveHinge
                            and cell.developed_module._absolute_rotation == 1
                        ):
                            absolute_rotation = 1
                    if (
                        module_type == Brick
                        and type(cell.developed_module) == ActiveHinge
                        and cell.developed_module._absolute_rotation == 1
                    ):
                        orientation = 1

                    #   print(orientation, absolute_rotation)
                    new_module = module_type(orientation * (math.pi / 2.0))
                    self.quantity_modules += 1
                    new_module._absolute_rotation = absolute_rotation
                    new_module.rgb = self.get_color(module_type, orientation)
                    new_module._parent = cell.developed_module
                    new_module.substrate_coordinates = potential_module_coord
                    new_module.turtle_direction = turtle_direction
                    new_module.direction_from_parent = slot
                    cell.developed_module.children[slot] = new_module
                    self.queried_substrate[potential_module_coord] = new_module

                    self.new_cell(cell, new_module, slot)
            #     else:
            #         print('intersecting or full!', potential_module_coord)
            # else:
            #     print('no slots!')

    def new_cell(self, source_cell: Cell, new_module: Module, slot: int):
        #  print('new')
        new_cell = Cell()

        # share concentrations in diffusion sites
        for tf in source_cell.transcription_factors:
            #  print('old cell', tf, source_cell.transcription_factors[tf], sum(source_cell.transcription_factors[tf]))

            new_cell.transcription_factors[tf] = [0, 0, 0, 0]

            # in the case of joint, shares also concentrations of sites without slot
            if type(source_cell.developed_module) == ActiveHinge:
                sites = [Core.LEFT, Core.FRONT, Core.RIGHT]
                for s in sites:
                    if source_cell.transcription_factors[tf][s] > 0:
                        half_concentration = (
                            source_cell.transcription_factors[tf][s] / 2
                        )
                        source_cell.transcription_factors[tf][s] = half_concentration
                        new_cell.transcription_factors[tf][
                            Core.BACK
                        ] += half_concentration
                new_cell.transcription_factors[tf][Core.BACK] /= len(sites)
            else:
                if source_cell.transcription_factors[tf][slot] > 0:
                    half_concentration = source_cell.transcription_factors[tf][slot] / 2
                    source_cell.transcription_factors[tf][slot] = half_concentration
                    new_cell.transcription_factors[tf][Core.BACK] = half_concentration

            #  print('new cell', tf, new_cell.transcription_factors[tf], sum(new_cell.transcription_factors[tf]))

        # print('\n mod', new_module, 'at',slot)
        self.express_promoters(new_cell)
        self.cells.append(new_cell)
        new_cell.developed_module = new_module
        new_module.cell = new_cell

    def maternal_injection(self):
        # injects maternal tf into single cell embryo and starts development of the first cell
        # the tf injected is regulatory tf of the first gene in the genetic string
        # the amount inject is the minimum for the regulatory tf to regulate its regulated product
        first_gene_idx = 0
        tf_label_idx = 0
        min_value_idx = 1
        # TODO: do not inject nor grow if there are no promotors (unlikely)
        mother_tf_label = self.promotors[first_gene_idx][tf_label_idx]
        mother_tf_injection = float(self.promotors[first_gene_idx][min_value_idx])

        first_cell = Cell()
        # distributes injection among diffusion sites
        first_cell.transcription_factors[mother_tf_label] = [
            mother_tf_injection / self.diffusion_sites_qt
        ] * self.diffusion_sites_qt
        # print('\n head', mother_tf_label, mother_tf_injection)
        self.express_promoters(first_cell)
        self.cells.append(first_cell)
        first_cell.developed_module = self.place_head(first_cell)

    def express_promoters(self, new_cell: Cell):
        for promotor in self.promotors:
            regulatory_min_val = min(
                float(promotor[self.regulatory_min_idx]),
                float(promotor[self.regulatory_max_idx]),
            )
            regulatory_max_val = max(
                float(promotor[self.regulatory_min_idx]),
                float(promotor[self.regulatory_max_idx]),
            )
            # print(promotor[self.regulatory_transcription_factor_idx])
            # expresses a tf if its regulatory tf is present and within a range
            if (
                new_cell.transcription_factors.get(
                    promotor[self.regulatory_transcription_factor_idx]
                )
                and sum(
                    new_cell.transcription_factors[
                        promotor[self.regulatory_transcription_factor_idx]
                    ]
                )
                >= regulatory_min_val
                and sum(
                    new_cell.transcription_factors[
                        promotor[self.regulatory_transcription_factor_idx]
                    ]
                )
                <= regulatory_max_val
            ):
                # update or add
                if new_cell.transcription_factors.get(
                    promotor[self.transcription_factor_idx]
                ):
                    new_cell.transcription_factors[
                        promotor[self.transcription_factor_idx]
                    ][int(promotor[self.diffusion_site_idx])] += float(
                        promotor[self.transcription_factor_amount_idx]
                    )
                else:
                    new_cell.transcription_factors[
                        promotor[self.transcription_factor_idx]
                    ] = [0] * self.diffusion_sites_qt
                    new_cell.transcription_factors[
                        promotor[self.transcription_factor_idx]
                    ][int(promotor[self.diffusion_site_idx])] = float(
                        promotor[self.transcription_factor_amount_idx]
                    )

    def place_head(self, new_cell: Cell) -> Core:
        module_type = Core
        self.phenotype_body = Body()
        orientation = 0
        self.phenotype_body.core._rotation = orientation
        self.phenotype_body.core.rgb = self.get_color(module_type, orientation)
        self.phenotype_body.core.substrate_coordinates = (0, 0)
        self.phenotype_body.core.turtle_direction = Core.FRONT
        self.phenotype_body.core.cell = new_cell
        self.queried_substrate[(0, 0)] = self.phenotype_body.core

        return self.phenotype_body.core

    def get_color(
        self,
        module_type: Union[type[Brick], type[ActiveHinge], type[Core]],
        rotation: int,
    ) -> List[float]:
        if module_type == Brick:
            return [0, 0, 1]
        elif module_type == ActiveHinge:
            if rotation == 0:
                return [1, 0.08, 0.58]
            else:
                return [0.7, 0, 0]
        elif module_type == Core:
            return [1, 1, 0]
        else:
            raise ValueError(f"{module_type} is not a valid Module type")

    def calculate_coordinates(
        self, parent: Module, slot: Directions
    ) -> Tuple[Tuple[int, int], int]:
        # calculate the actual 2d direction and coordinates of new module using relative-to-parent position as reference
        dic = {Core.FRONT: 0, Core.LEFT: 1, Core.BACK: 2, Core.RIGHT: 3}

        inverse_dic = {0: Core.FRONT, 1: Core.LEFT, 2: Core.BACK, 3: Core.RIGHT}

        direction = dic[parent.turtle_direction] + dic[slot]
        if direction >= len(dic):
            direction = direction - len(dic)

        turtle_direction = inverse_dic[direction]
        if turtle_direction == Core.LEFT:
            coordinates = (
                parent.substrate_coordinates[0] - 1,
                parent.substrate_coordinates[1],
            )
        elif turtle_direction == Core.RIGHT:
            coordinates = (
                parent.substrate_coordinates[0] + 1,
                parent.substrate_coordinates[1],
            )
        elif turtle_direction == Core.FRONT:
            coordinates = (
                parent.substrate_coordinates[0],
                parent.substrate_coordinates[1] + 1,
            )
        elif turtle_direction == Core.BACK:
            coordinates = (
                parent.substrate_coordinates[0],
                parent.substrate_coordinates[1] - 1,
            )
        else:
            raise ValueError("Unreachable")

        return coordinates, turtle_direction