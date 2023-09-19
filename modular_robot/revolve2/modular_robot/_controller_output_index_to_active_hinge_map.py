from ._active_hinge import ActiveHinge


class ControllerOutputIndexToActiveHingeMap:
    _inner_mapping: dict[int, ActiveHinge]

    def __init__(self) -> None:
        self._inner_mapping = {}

    def add(self, controller_output_index: int, active_hinge: ActiveHinge) -> None:
        self._inner_mapping[controller_output_index] = active_hinge

    def map(self, controller_output_index: int) -> ActiveHinge:
        return self._inner_mapping[controller_output_index]
