from revolve.evosphere.adaptations.coppelia_evosphere import CoppeliaEvosphere
from revolve.evosphere.ecosphere import CoppeliaEcosphere
from simulation.simulator.adapter.vrep.coppelia_simulator_adapter import CoppeliaSimulatorAdapter

if __name__ == "__main__":

    vrep = CoppeliaSimulatorAdapter(CoppeliaEcosphere("robobo"))
    print(vrep.environment.robobo.simulator.client_id)
    print("finished")
    vrep._disconnect()

    evosphere = CoppeliaEvosphere()
    evosphere.evolve()
