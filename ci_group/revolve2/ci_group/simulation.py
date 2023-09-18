"""Standard simulation functions and parameters."""
from revolve2.simulation.simulator import BatchParameters

STANDARD_SIMULATION_TIME = 30
STANDARD_SAMPLING_FREQUENCY = 0.0001
STANDARD_SIMULATION_TIMESTEP = 0.001
STANDARD_CONTROL_FREQUENCY = 60

STANDARD_BATCH_PARAMETERS = BatchParameters(
    simulation_time=STANDARD_SIMULATION_TIME,
    sampling_frequency=STANDARD_SAMPLING_FREQUENCY,
    simulation_timestep=STANDARD_SIMULATION_TIMESTEP,
    control_frequency=STANDARD_CONTROL_FREQUENCY,
)
