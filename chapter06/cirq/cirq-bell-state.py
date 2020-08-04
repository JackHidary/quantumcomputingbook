"""Script for preparing the Bell state |\Phi^{+}> in Cirq."""

# Import the Cirq library
import cirq

# Get qubits and circuit
qreg = [cirq.LineQubit(x) for x in range(2)]
circ = cirq.Circuit()

# Add the Bell state preparation circuit
circ.append([cirq.H(qreg[0]), 
             cirq.CNOT(qreg[0], qreg[1])])

# Display the circuit
print("Circuit")
print(circ)

# Add measurements
circ.append(cirq.measure(*qreg, key="z"))

# Simulate the circuit
sim = cirq.Simulator()
res = sim.run(circ, repetitions=100)

# Display the outcomes
print("\nMeasurements:")
print(res.histogram(key="z"))