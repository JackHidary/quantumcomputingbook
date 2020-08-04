"""Example using QAOA to solve MaxCut from Chapter 9.3.

Requirements:
cirq==0.7.0
"""

# Imports
import numpy as np
import matplotlib.pyplot as plt

import cirq


# Function to implement a ZZ gate on qubits a, b with angle gamma
def ZZ(a, b, gamma):
    """Returns a circuit implementing exp(-i \pi \gamma Z_i Z_j)."""
    # Get a circuit
    circuit = cirq.Circuit()

    # Gives the fourth diagonal component
    circuit.append(cirq.CZ(a, b) ** gamma)

    # Gives the third diagonal component
    circuit.append([cirq.X(b), cirq.CZ(a, b) ** (-1 * gamma), cirq.X(b)])

    # Gives the second diagonal component
    circuit.append([cirq.X(a), cirq.CZ(a, b) ** -gamma, cirq.X(a)])

    # Gives the first diagonal component
    circuit.append([cirq.X(a), cirq.X(b), cirq.CZ(a, b) ** gamma,
                    cirq.X(a), cirq.X(b)])

    return circuit


# 26.s.one
# Make sure the circuit gives the correct matrix
qreg = cirq.LineQubit.range(2)
zzcirc = ZZ(qreg[0], qreg[1], 0.5)
print("Circuit for ZZ gate:", zzcirc, sep="\n")
print("\nUnitary of circuit:", zzcirc.unitary().round(2), sep="\n")

ncols = 2
nrows = 2
qreg = [[cirq.GridQubit(i,j) for j in range(ncols)] for i in range(nrows)]

# Function to implement the cost Hamiltonian
def cost_circuit(gamma):
    """Returns a circuit for the cost Hamiltonian."""
    circ = cirq.Circuit()
    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1:
                circ += ZZ(qreg[i][j], qreg[i + 1][j], gamma)
            if j < ncols - 1:
                circ += ZZ(qreg[i][j], qreg[i][j + 1], gamma)

    return circ

# Function to implement the mixer Hamiltonian
def mixer(beta):
  """Generator for U(H_B, beta) layer (mixing layer)"""
  for row in qreg:
    for qubit in row:
      yield cirq.X(qubit)**beta


# Function to build the QAOA circuit
def qaoa(gammas, betas):
    """Returns a QAOA circuit."""
    circ = cirq.Circuit()
    circ.append(cirq.H.on_each(*[q for row in qreg for q in row]))

    for i in range(len(gammas)):
        circ += cost_circuit(gammas[i])
        circ.append(mixer(betas[i]))

    return circ

def simulate(circ):
    """Returns the wavefunction after applying the circuit."""
    sim = cirq.Simulator()
    return sim.simulate(circ).final_state


def energy_from_wavefunction(wf):
    """Computes the energy-per-site of the Ising Model from the wavefunction."""
    # Z is a (n_sites x 2**n_sites) array. Each row consists of the
    # 2**n_sites non-zero entries in the operator that is the Pauli-Z matrix on
    # one of the qubits times the identites on the other qubits. The (i*n_cols + j)th
    # row corresponds to qubit (i,j).
    nsites = nrows * ncols
    Z = np.array([(-1) ** (np.arange(2 ** nsites) >> i)
                  for i in range(nsites - 1, -1, -1)])

    # Create the operator corresponding to the interaction energy summed over all
    # nearest-neighbor pairs of qubits
    ZZ_filter = np.zeros_like(wf, dtype=float)
    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1:
                ZZ_filter += Z[i * ncols + j] * Z[(i + 1) * ncols + j]
            if j < ncols - 1:
                ZZ_filter += Z[i * ncols + j] * Z[i * ncols + (j + 1)]

    # Expectation value of the energy divided by the number of sites
    return -np.sum(np.abs(wf) ** 2 * ZZ_filter) / nsites

def cost(gammas, betas):
    """Returns the cost function of the problem."""
    wavefunction = simulate(qaoa(gammas, betas))
    return energy_from_wavefunction(wavefunction)


def grid_search(gammavals, betavals):
    """Does a grid search over all parameter values."""
    costmat = np.zeros((len(gammavals), len(betavals)))

    for (i, gamma) in enumerate(gammavals):
        for (j, beta) in enumerate(betavals):
            costmat[i, j] = cost([gamma], [beta])

    return costmat

# Get a range of parameters
gammavals = np.linspace(0, 1.0, 50)
betavals = np.linspace(0, np.pi, 75)

# Compute the cost at all parameter values using a grid search
costmat = grid_search(gammavals, betavals)

# Plot the cost landscape
plt.imshow(costmat, extent=(0, 1, 0, np.pi), origin="lower", aspect="auto")
plt.colorbar()
plt.show()

# Coordinates from the grid of cost values
gamma_coord, beta_coord = np.where(costmat == np.min(costmat))

# Values from the coordinates
gamma_opt = gammavals[gamma_coord[0]]
beta_opt = betavals[beta_coord[0]]


def get_bit_strings(gammas, betas, nreps=10000):
    """Measures the QAOA circuit in the computational basis to get bitstrings."""
    circ = qaoa(gammas, betas)
    circ.append(
        cirq.measure(*[qubit for row in qreg for qubit in row], key='m'))

    # Simulate the circuit
    sim = cirq.Simulator()
    res = sim.run(circ, repetitions=nreps)

    return res

# Sample to get bits and convert to a histogram
bits = get_bit_strings([gamma_opt], [beta_opt])
hist = bits.histogram(key="m")

# Get the most common bits
top = hist.most_common(2)

# Print out the two most common bitstrings measured
print("\nMost common bitstring:")
print(format(top[0][0], "#010b"))

print("\nSecond most common bitstring:")
print(bin(top[1][0]))

