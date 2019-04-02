"""Quantum chemistry (simulation) example using OpenFermion and Cirq."""

# Imports
import numpy
import scipy

import cirq
import openfermion
import openfermioncirq

# Set the number of qubits, simulation time, and seed for reproducibility
n_qubits = 3
simulation_time = 1.0
random_seed = 8317

# =============================
# Get a Hamiltonian to simulate
# =============================

# Generate the random one-body operator
T = openfermion.random_hermitian_matrix(n_qubits, seed=random_seed)
print("Hamiltonian:", T, sep="\n")

# Compute the OpenFermion "FermionOperator" form of the Hamiltonian
H = openfermion.FermionOperator()
for p in range(n_qubits):
    for q in range(n_qubits):
        term = ((p, 1), (q, 0))
        H += openfermion.FermionOperator(term, T[p, q])
print("\nFermion operator:")
print(H)

# Diagonalize T and obtain basis transformation matrix (aka "u")
eigenvalues, eigenvectors = numpy.linalg.eigh(T)
basis_transformation_matrix = eigenvectors.transpose()

# Initialize the qubit register
qubits = cirq.LineQubit.range(n_qubits)

# Rotate to the eigenbasis
inverse_basis_rotation = cirq.inverse(
    openfermioncirq.bogoliubov_transform(qubits, basis_transformation_matrix)
)
circuit = cirq.Circuit.from_ops(inverse_basis_rotation)

# Print the circuit for rotating to the eigenbasis
print("\nCircuit:")
print(circuit)

# Add diagonal phase rotations to circuit
for k, eigenvalue in enumerate(eigenvalues):
    phase = -eigenvalue * simulation_time
    circuit.append(cirq.Rz(rads=phase).on(qubits[k]))

# Finally, change back to the computational basis
basis_rotation = openfermioncirq.bogoliubov_transform(
    qubits, basis_transformation_matrix
)
circuit.append(basis_rotation)

# ================================================================
# Get a random initial state to apply the Hamiltonian evolution to
# ================================================================

# Initialize a random initial state
initial_state = openfermion.haar_random_vector(
    2 ** n_qubits, random_seed).astype(numpy.complex64)

# ===================================
# Simulate the evolution analytically
# ===================================

# Numerically compute the correct circuit output
hamiltonian_sparse = openfermion.get_sparse_operator(H)
exact_state = scipy.sparse.linalg.expm_multiply(
    -1j * simulation_time * hamiltonian_sparse, initial_state
)

# ======================================================
# Simulate the evolution on a quantum computer simulator
# ======================================================

# Use Cirq simulator to apply circuit
simulator = cirq.google.XmonSimulator()
result = simulator.simulate(circuit, qubit_order=qubits,
                            initial_state=initial_state)
simulated_state = result.final_state

# Print final fidelity
fidelity = abs(numpy.dot(simulated_state, numpy.conjugate(exact_state)))**2
print("\nfidelity =", round(fidelity, 4))

# ===============================================
# Compile the circuit for different architectures
# ===============================================

# Compile the circuit to Google's Xmon architecture
xmon_circuit = cirq.google.optimized_for_xmon(circuit)
print("\nCircuit optimized for Xmon:")
print(xmon_circuit)

# Print out the OpenQASM code for IBM's hardware
print("\nOpenQASM code:")
print(xmon_circuit.to_qasm())
