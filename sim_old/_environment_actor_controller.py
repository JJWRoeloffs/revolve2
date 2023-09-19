"""Contains EnvironmentBrain, an environment controller for an environment with a single actor that uses a provided Brain."""

from revolve2.controllers import Brain
from revolve2.simulation.running import ActorControl, EnvironmentController


class EnvironmentBrain(EnvironmentController):
    """An environment controller for an environment with a single actor that uses a provided Brain."""

    brain: Brain

    def __init__(self, brain: Brain) -> None:
        """
        Initialize this object.

        :param brain: The actor controller to use for the single actor in the environment.
        """
        self.brain = brain

    def control(self, dt: float, actor_control: ActorControl) -> None:
        """
        Control the single actor in the environment using an Brain.

        :param dt: Time since last call to this function.
        :param actor_control: Object used to interface with the environment.
        """
        self.brain.step(dt)
        actor_control.set_dof_targets(0, self.brain.get_dof_targets())
