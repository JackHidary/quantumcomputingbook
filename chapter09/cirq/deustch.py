"""Deustch-Jozsa algorithm."""

# Import the Cirq Library
import cirq

# Get two qubits, a data qubit and target qubit, respectively
q0, q1 = cirq.LineQubit.range(2)

# Dictionary of oracles
oracles = {'0': [], '1': [cirq.X(q1)], 'x': [cirq.CNOT(q0, q1)],
           'notx': [cirq.CNOT(q0, q1), cirq.X(q1)]}

def deutsch_algorithm(oracle):
    """Yields a circuit for Deustch's algorithm given operations implementing
    the oracle."""
    yield cirq.X(q1)
    yield cirq.H(q0), cirq.H(q1)
    yield oracle
    yield cirq.H(q0)
    yield cirq.measure(q0)

# Display each circuit for all oracles
for key, oracle in oracles.items():
    print('Circuit for {}...'.format(key))
    print(cirq.Circuit(deutsch_algorithm(oracle)), end="\n\n")

# Get a simulator
simulator = cirq.Simulator()

# Execute the circuit for each oracle to distingiush constant from balanced
for key, oracle in oracles.items():
    result = simulator.run(
        cirq.Circuit(deutsch_algorithm(oracle)),
        repetitions=10
    )
    print('oracle: {:<4} results: {}'.format(key, result))
