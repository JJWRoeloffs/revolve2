import unittest

from nca.core.actor.actors import Actors
from simulation.simulator.simulator_command import SimulateCommand, TaskPriority
from simulation.simulator.simulator_factory import SimulatorFactory

from evosphere.mock_ecosphere import MockEcosphere
from simulation_test.simulator.test_connector_adapter import TestConnectorAdapter


class SimulationSupervisorTest(unittest.TestCase):

    def test_none(self):
        request_command = SimulateCommand(Actors(), MockEcosphere(), TaskPriority.MEDIUM)

        factory = SimulatorFactory(request_command)
        connector = factory.create()

        self.assertIsInstance(connector, TestConnectorAdapter)

    """
    def test_gazebo(self):
        request_command = RequestCommand(TestEnvironment(), SimulatorType.GAZEBO, TaskPriority.MEDIUM)

        factory = SimulatorFactory(request_command)
        connector = factory.create()

        self.assertIsInstance(connector, GazeboConnectorAdapter)
    """