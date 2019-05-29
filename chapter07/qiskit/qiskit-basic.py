"""Simple program in Qiskit."""

# Import the Qiskit package
import qiskit

# Create a quantum register with one qubit
qreg = qiskit.QuantumRegister(1, name='qreg')

# Create a classical register with one qubit
creg = qiskit.ClassicalRegister(1, name='creg')

# Create a quantum circuit with the above registers
circ = qiskit.QuantumCircuit(qreg, creg)

# Add a NOT operation on the qubit
circ.x(qreg[0])

# Add a measurement on the qubit
circ.measure(qreg, creg)

# Print the circuit
print(circ.draw())

# Get a backend to run on
backend = qiskit.BasicAer.get_backend("qasm_simulator")

# Execute the circuit on the backend and get the measurement results
job = qiskit.execute(circ, backend, shots=10)
result = job.result()

# Print the measurement results
print(result.get_counts())
