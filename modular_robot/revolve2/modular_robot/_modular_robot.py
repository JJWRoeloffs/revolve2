from ._brain import Brain
from ._body import Body


class ModularRobot:
    """A module robot consisting of a body and brain."""

    body: Body
    brain: Brain

    def __init__(self, body: Body, brain: Brain):
        """
        Initialize this object.

        :param body: The body of the modular robot.
        :param brain: The brain of the modular robot.
        """
        self.body = body
        self.brain = brain
