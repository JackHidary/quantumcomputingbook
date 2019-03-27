"""Deustch-Jozsa algorithm in Cirq."""

# Import the Cirq library
import cirq

# Get three qubits -- two data and one target qubit
q0, q1, q2 = cirq.LineQubit.range(3)

# Oracles for constant functions
constant = ([], [cirq.X(q2)])

# Oracles for balanced functions
balanced = ([cirq.CNOT(q0, q2)], 
            [cirq.CNOT(q1, q2)], 
            [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2)],
            [cirq.CNOT(q0, q2), cirq.X(q2)], 
            [cirq.CNOT(q1, q2), cirq.X(q2)], 
            [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2), cirq.X(q2)])


def your_circuit(oracle):
    """Yields a circiut for the Deustch-Jozsa algorithm on three qubits."""
    # phase kickback trick
    yield cirq.X(q2), cirq.H(q2)
    
    # equal superposition over input bits
    yield cirq.H(q0), cirq.H(q1)
    
    # query the function
    yield oracle
    
    # interference to get result, put last qubit into |1>
    yield cirq.H(q0), cirq.H(q1), cirq.H(q2)
    
    # a final OR gate to put result in final qubit
    yield cirq.X(q0), cirq.X(q1), cirq.CCX(q0, q1, q2)
    yield cirq.measure(q2)
    
# Get a simulator
simulator = cirq.Simulator()

# Execute circuit for oracles of constant value functions
print('Your result on constant functions')
for oracle in constant:
    result = simulator.run(cirq.Circuit.from_ops(your_circuit(oracle)), repetitions=10)
    print(result)
    
# Execute circuit for oracles of balanced functions
print('Your result on balanced functions')
for oracle in balanced:
    result = simulator.run(cirq.Circuit.from_ops(your_circuit(oracle)), repetitions=10)
    print(result)
