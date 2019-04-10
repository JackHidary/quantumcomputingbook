"""Quantum supremacy circuits in Cirq."""

# Imports
import cirq

# Number of rows in grid of qubits
nrows = 4

# Number of columns in grid of qubits
ncols = 4

# Depth of CZ gates in supremacy circuit
depth = 5

supremacy_circuit = cirq.experiments.generate_supremacy_circuit_google_v2_grid(
    nrows, ncols, depth, seed=123
)

print(supremacy_circuit)

