"""Superdense coding."""

# Imports
import qiskit

# Create two quantum and classical registers
qreg = qiskit.QuantumRegister(2)
creg = qiskit.ClassicalRegister(2)
circ = qiskit.QuantumCircuit(qreg, creg)

# Add a Hadamard gate on qubit 0 to create a superposition
circ.h(qreg[0])

# Apply the X operator to qubit 0
circ.x(qreg[0])

# To get the Bell state apply the CNOT operator on qubit 0 and 1
circ.cx(qreg[0], qreg[1])

# Apply the H operator to take qubit 0 out of superposition
circ.h(qreg[0])

# Add a Measure gate to obtain the message
circ.measure(qreg, creg)

# Print out the circuit
print("Circuit:")
print(circ.draw())

# Run the quantum circuit on a simulator backend
backend = qiskit.Aer.get_backend("statevector_simulator")
job = qiskit.execute(circ, backend)
res = job.result()
print(res.get_counts())
