"""Continuous time quantum walk in pyQuil."""

# Imports
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.linalg import expm

import pyquil.quil as pq
import pyquil.api as api
from pyquil.gates import H, X, CPHASE00

# =============================================================================
# Classical setup
# =============================================================================

# Create a graph
G = nx.complete_graph(4)
nx.draw_networkx(G)

# Diagonalize the adjacency matrix
A = nx.adjacency_matrix(G).toarray()
eigvals, _ = np.linalg.eigh(A)
print("Eigenvalues =", eigvals)

# Get the Hamiltonian
ham = A + np.eye(4)
print(ham)

# Hadamard gate
hgate = np.sqrt(1/2) * np.array([[1, 1], [1, -1]])

# Form the matrix Q = H \otimes H to diagonalize the Hamiltonian
Q = np.kron(hgate, hgate)

# Print out the Q^\dagger H Q to verify it's diagonal
diag = Q.conj().T.dot(ham).dot(Q)
print("$Q^\dagger * H * Q = $")
print(diag)

# =============================================================================
# Quantum walk and classical walk
# =============================================================================

# Get a simulator
qvm = api.QVMConnection()

# Function for a the continuous time quantum walk circuit on a complete graph
def k_4_ctqw(t):
    """Returns a program implementing a continuous time quantum walk."""
    prog = pq.Program()
    
    # Change to diagonal basis
    prog.inst(H(0))
    prog.inst(H(1))
    
    # Time evolve
    prog.inst(CPHASE00(-4*t, 0, 1))
    
    # Change back to computational basis
    prog.inst(H(0))
    prog.inst(H(1))
    
    return prog

# Stochastic transition matrix for classical walk
M = A / np.sum(A, axis=0)

# Set up time to simulate for
tmax = 4
steps = 40
time = np.linspace(0, tmax, steps)

# Arrays to hold quantum probabilities and classical probabilities at each time
quantum_probs = np.zeros((steps, tmax))
classical_probs = np.zeros((steps, tmax))

# Do the classical and quantum continuous-time walks
for i, t in enumerate(time):
    # Get a quantum program
    prog = k_4_ctqw(t)
    
    # Simulate the circuit and store the probabilities
    wvf = qvm.wavefunction(prog)
    vec = wvf.amplitudes
    quantum_probs[i] = np.abs(vec)**2

    # Do the classical continuous time walk
    classical_ev = expm((M-np.eye(4))*t)
    classical_probs[i] = classical_ev[:, 0]

# =============================================================================
# Plotting
# =============================================================================
    
_, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=True)

ax1.set_title("Quantum evolution")
ax1.set_ylabel("Probability")
ax1.plot(time, quantum_probs[:, 0], label='Initial node')
ax1.plot(time, quantum_probs[:, 1], label='Remaining nodes')
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

ax2.set_title("Classical evolution")
ax2.set_xlabel('t')
ax2.set_ylabel("Probability")
ax2.plot(time, classical_probs[:, 0], label='Initial node')
ax2.plot(time, classical_probs[:, 1], label='Remaining nodes')


def k_2n_ctqw(n, t):
    p = pq.Program()
    
    #    Change to diagonal basis
    for i in range(n):
        p.inst(H(i))
        p.inst(X(i))

    #   Create and apply CPHASE00
    big_cphase00 = np.diag(np.ones(2**n)) + 0j
    big_cphase00[0, 0] = np.exp(-1j*4*t)
    p.defgate("BIG-CPHASE00", big_cphase00)     
    args = tuple(["BIG-CPHASE00"] + list(range(n)))
    p.inst(args)

    #   Change back to computational basis
    for i in range(n):
        p.inst(X(i))
        p.inst(H(i))
    
    return p

def k_2n_crw(n, t):
    G = nx.complete_graph(2**n)
    A = nx.adjacency_matrix(G)
    T = A / A.sum(axis=0)
    classical_ev = expm((T-np.eye(2**n))*t)
    
    return classical_ev[:, 0]    

time = np.linspace(0, 4, 40)
quantum_probs = np.zeros((len(time), 8))
classical_probs = np.zeros((len(time), 8))

for i, t in enumerate(time):
    p = k_2n_ctqw(3, t)  
    wvf = qvm.wavefunction(p)
    vec = wvf.amplitudes
    quantum_probs[i] = np.abs(vec)**2
    classical_probs[i] = k_2n_crw(3, t)  
    
f, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=True)

ax1.set_title("Quantum evolution")
ax1.set_ylabel('p')
ax1.plot(time, quantum_probs[:, 0], label='Initial node')
ax1.plot(time, quantum_probs[:, 1], label='Remaining nodes')
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

ax2.set_title("Classical evolution")
ax2.set_xlabel('t')
ax2.set_ylabel('p')
ax2.plot(time, classical_probs[:, 0], label='Initial node')
ax2.plot(time, classical_probs[:, 1], label='Remaining nodes')
