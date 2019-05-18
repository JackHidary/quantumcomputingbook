"""Quantum phase estimation (QPE) in Cirq."""

# Imports
import numpy as np
from scipy.stats import unitary_group

import cirq

# =============================================================================
# Helper functions
# =============================================================================

def binary_decimal(string):
    """Returns the numeric value of 0babc... where a, b, c, ... are bits.
    
    Examples:
        0b10 --> 0.5
        0b01 --> 0.25
    """
    val = 0.0
    for (ind, bit) in enumerate(string[2:]):
        if int(bit) == 1:
            val += 2**(-1 -ind)
    return val

# =============================================================================
# Input to QPE
# =============================================================================

# Set seed for reproducible results
np.random.seed(123)

# Get a random unitary matrix on two qubits
m = 2
dim = 2**m
unitary = unitary_group.rvs(dim)

unitary = np.identity(4)

xmat = np.array([[0, 1], [1, 0]])
zmat = np.array([[1, 0], [0, -1]])
unitary = np.kron(xmat, zmat)

# Print it to the console
print("Unitary:")
print(unitary)

# Diagonalize it classically
evals, evecs = np.linalg.eig(unitary)

# =============================================================================
# Building the circuit for QPE
# =============================================================================

# Number of qubits in the readout/answer register (# bits of precision)
n = 8

# Readout register
regA = cirq.LineQubit.range(n)

# Register for the eigenstate
regB = cirq.LineQubit.range(n, n + m)

# Get a circuit
circ = cirq.Circuit()

# Hadamard all qubits in the readout register
circ.append(cirq.H.on_each(regA))

# Hadamard all qubits in the second register
#circ.append(cirq.H.on_each(regB))

# Get a Cirq gate for the unitary matrix
ugate = cirq.ops.matrix_gates.TwoQubitMatrixGate(unitary)

# Controlled version of the gate
cugate = cirq.ops.ControlledGate(ugate)

# Do the controlled U^{2^k} operations
for k in range(n):
    circ.append(cugate(regA[k], *regB)**(2**k))

# Do the inverse QFT
for k in range(n - 1):
    circ.append(cirq.H.on(regA[k]))
    targ = k + 1
    for j in range(targ):
        exp = -2**(j - targ)
        rot = cirq.Rz(exp)
        crot = cirq.ControlledGate(rot)
        circ.append(crot(regA[j], regA[targ]))
circ.append(cirq.H.on(regA[n - 1]))

"""
# This is the QFT!
for k in reversed(range(n)):
    circ.append(cirq.H.on(regA[k]))
    for j in reversed(range(k)):
        exp = 2**(j - k)
        rot = cirq.Rz(exp)
        crot = cirq.ControlledGate(rot)
        circ.append(crot(regA[j], regA[k]))
"""

# Measure all qubits in the readout register
circ.append(cirq.measure(*regA, key="z"))

# Print out the circuit
#print("Circuit:")
#print(circ[5:])

# =============================================================================
# Executing the circuit for QPE
# =============================================================================

sim = cirq.Simulator()

res = sim.run(circ, repetitions=1000)

hist = res.histogram(key="z")

top = hist.most_common(2)

estimated = [np.exp(2j * np.pi * binary_decimal(bin(x[0]))) for x in top]

print("\nEigenvalues from QPE:")
print(sorted(estimated, key=lambda x: abs(x)**2))

print("\nActual eigenvalues:")
print(sorted(evals, key=lambda x: abs(x)**2))
