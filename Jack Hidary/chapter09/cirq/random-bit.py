"""Program for generating random bits in Cirq."""

# Imports
import cirq

# Helper function for visualizing output
def bitstring(bits):
    return ''.join('1' if e else '0' for e in bits)

# Get a qubit and quantum circuit
qbit = cirq.LineQubit(0)
circ = cirq.Circuit()

# Add the Hadamard and measure operations to the circuit
circ.append([cirq.H(qbit), cirq.measure(qbit, key="z")])

# Simulate the circuit
sim = cirq.Simulator()
res = sim.run(circ, repetitions=10)

# Print the outcome
print("Bitstring =", bitstring(res.measurements["z"]))
