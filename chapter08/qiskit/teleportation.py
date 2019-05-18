"""Quantum teleportation in Qiskit."""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
#from qiskit import available_backends, execute

# Create quantum and classical registers
q = QuantumRegister(3)
c = ClassicalRegister(3)
qc = QuantumCircuit(q, c)

# Create an initial superposition + state
qc.h(q[0])

# Take the qubit out of superposition
qc.h(q[0])

# Perform a CNOT between the qubits
qc.cx(q[0], q[1])

# Put the qubits into superposition and now the states are the same
qc.h(q[0])
qc.h(q[1])

# Prepare an initial state for qubit using a single unitary
qc.u1(0.5, q[0])

# Perform a CNOT between qubit 0 and qubit 1
qc.cx(q[0], q[1])

# Measure qubit  in the + - basis
qc.h(q[0])
qc.measure(q[0], c[0])

# If needed Perform a phase correction to qubit 1
if c[0] == 1:
   qc.z(q[1])

# Prepare an initial state for qubit 0 using a single unitary
qc.u1(0.5, q[0])

# Prepare an entangled pair using qubit 1 and qubit 2
qc.h(q[1])
qc.cx(q[1], q[2])

# Barrier to prevent gate reordering for optimization
qc.barrier(q)

# Perform a CNOT between qubit 0 and qubit 1
qc.cx(q[0], q[1])

# Measure qubit 1 in the computational basis
qc.measure(q[1], c[1])
# If needed Perform a bit flip correction to qubit 2
if c[1] == 1:
    qc.x(q[2])
 
# Measure qubit 0 in the + - basis
qc.h(q[0])
qc.measure(q[0], c[0])
# If needed Perform a phase correction to qubit 2
if c[0] == 1:
    qc.z(q[2])

print(qc.draw())