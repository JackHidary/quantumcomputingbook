"""Quantum phase estimation (QPE) in Cirq."""

# Imports
import numpy as np

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

# Number of qubits and dimension of the eigenstate
m = 2

# Get a unitary matrix on two qubits
xmat = np.array([[0, 1], [1, 0]])
zmat = np.array([[1, 0], [0, -1]])
unitary = np.kron(xmat, zmat)

# Print it to the console
print("Unitary:")
print(unitary)

# Diagonalize it classically
evals, _ = np.linalg.eig(unitary)

# =============================================================================
# Building the circuit for QPE
# =============================================================================

# Number of qubits in the readout/answer register (# bits of precision)
n = 2

# Readout register
regA = cirq.LineQubit.range(n)

# Register for the eigenstate
regB = cirq.LineQubit.range(n, n + m)

# Get a circuit
circ = cirq.Circuit()

# Hadamard all qubits in the readout register
circ.append(cirq.H.on_each(regA))

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

# Measure all qubits in the readout register
circ.append(cirq.measure(*regA, key="z"))

# Print out the circuit
print("Circuit:")
print(circ)

# =============================================================================
# Executing the circuit for QPE
# =============================================================================

# Get a simulator
sim = cirq.Simulator()

# Simulate the circuit and get the most frequent measurement outcomes
res = sim.run(circ, repetitions=1000)
hist = res.histogram(key="z")
top = hist.most_common(2)

# =============================================================================
# Compute the eigenvalues from QPE and compare them to the actual values
# =============================================================================

# Eigenvalues from QPE
estimated = [np.exp(2j * np.pi * binary_decimal(bin(x[0]))) for x in top]

# Print out the estimated eigenvalues
print("\nEigenvalues from QPE:")
print(set(sorted(estimated, key=lambda x: abs(x)**2)))

# Print out the actual eigenvalues
print("\nActual eigenvalues:")
print(set(sorted(evals, key=lambda x: abs(x)**2)))
