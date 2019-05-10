"""Program for generating random numbers in Cirq."""

# Imports
import cirq

# Number of qubits
n = 10

# Helper function for visualizing output
def bitstring(bits):
    return ''.join('1' if e else '0' for e in bits)

# Get a qubit and quantum circuit
qreg = [cirq.LineQubit(x) for x in range(n)]
circ = cirq.Circuit()

# Add the Hadamard and measure operations to the circuit
for x in range(n):
    circ.append([cirq.H(qreg[x]), cirq.measure(qreg[x])])

# Simulate the circuit
sim = cirq.Simulator()
res = sim.run(circ, repetitions=1)

# Print the measured bitstring
bits = bitstring(res.measurements.values())
print("Bitstring =", bits)

# Print the integer corresponding to the bitstring
print("Integer =", int(bits, 2))
