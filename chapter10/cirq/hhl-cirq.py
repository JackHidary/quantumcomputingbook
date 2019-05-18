"""HHL algorithm in Cirq, modified from

https://github.com/quantumlib/Cirq/blob/master/examples/hhl.py

Example of circuit with 2 register qubits.

(0, 0): ─────────────────────────Ry(θ₄)─Ry(θ₁)─Ry(θ₂)─Ry(θ₃)──────────────M──
                     ┌──────┐    │      │      │      │ ┌───┐
(1, 0): ─H─@─────────│      │──X─@──────@────X─@──────@─│   │─────────@─H────
           │         │QFT^-1│    │      │      │      │ │QFT│         │
(2, 0): ─H─┼─────@───│      │──X─@────X─@────X─@────X─@─│   │─@───────┼─H────
           │     │   └──────┘                           └───┘ │       │
(3, 0): ───e^iAt─e^2iAt───────────────────────────────────────e^-2iAt─e^-iAt─

References

Harrow, Aram W. et al. Quantum algorithm for solving linear systems of
equations, https://arxiv.org/abs/0811.3171.

Coles, Eidenbenz et al. Quantum Algorithm Implementations for Beginners,
https://arxiv.org/abs/1804.03719
"""

# =============================================================================
# Imports
# =============================================================================

import math
import numpy as np
import cirq

# =============================================================================
# Helper classes for building the HHL circuit
# =============================================================================


class HamiltonianSimulation(cirq.EigenGate, cirq.SingleQubitGate):
    """A gate that implements e^iAt.
    
    If a large matrix is used, the circuit should implement actual Hamiltonian 
    simulation, for example by using the linear operators framework in Cirq.
    """

    def __init__(self, A, t, exponent=1.0):
        """Initializes a HamiltonianSimulation.
        
        Args:
            A : numpy.ndarray
                Hermitian matrix that defines the linear system Ax = b.
            
            t : float
                Simulation time. Hyperparameter of HHL.
        """
        cirq.SingleQubitGate.__init__(self)
        cirq.EigenGate.__init__(self, exponent=exponent)
        self.A = A
        self.t = t
        ws, vs = np.linalg.eigh(A)
        self.eigen_components = []
        for w, v in zip(ws, vs.T):
            theta = w*t / math.pi
            P = np.outer(v, np.conj(v))
            self.eigen_components.append((theta, P))

    def _with_exponent(self, exponent):
        return HamiltonianSimulation(self.A, self.t, exponent)

    def _eigen_components(self):
        return self.eigen_components

class PhaseKickback(cirq.Gate):
    """A gate for the phase kickback stage of Quantum Phase Estimation.
    
    Consists of a series of controlled e^iAt gates with the memory qubit as
    the target and each register qubit as the control, raised
    to the power of 2 based on the qubit index.
    """

    def __init__(self, num_qubits, unitary):
        """Initializes a PhaseKickback gate.
        
        Args:
            num_qubits : int
                The number of qubits in the readout register + 1.
                
                Note: The last qubit stores the eigenvector; all other qubits 
                      store the estimated phase, in big-endian.

            unitary : numpy.ndarray
                The unitary gate whose phases will be estimated.
        """
        super(PhaseKickback, self)
        self._num_qubits = num_qubits
        self.U = unitary

    def num_qubits(self):
        """Returns the number of qubits."""
        return self._num_qubits

    def _decompose_(self, qubits):
        """Generator for the phase kickback circuit."""
        qubits = list(qubits)
        memory = qubits.pop()
        for i, qubit in enumerate(qubits):
            yield cirq.ControlledGate(self.U**(2**i))(qubit, memory)


class QFT(cirq.Gate):
    """Quantum gate for the Quantum Fourier Transformation.
    
    Note: Swaps are omitted here. These are implicitly done in the 
    PhaseKickback gate by reversing the control qubit order.
    """

    def __init__(self, num_qubits):
        """Initializes a QFT circuit.
        
        Args:
            num_qubits : int
                Number of qubits.
        """
        super(QFT, self)
        self._num_qubits = num_qubits

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        processed_qubits = []
        for q_head in qubits:
            for i, qubit in enumerate(processed_qubits):
                yield cirq.CZ(qubit, q_head)**(1/2.0**(i+1))
            yield cirq.H(q_head)
            processed_qubits.insert(0, q_head)


class QPE(cirq.Gate):
    """A gate for Quantum Phase Estimation."""

    def __init__(self, num_qubits, unitary):
        """Initializes an HHL circuit.
        
        Args:
            num_qubits : int
                The number of qubits in the readout register.
                
                Note: The last qubit stores the eigenvector; all other qubits 
                      store the estimated phase, in big-endian.

            unitary : numpy.ndarray
                The unitary gate whose phases will be estimated.
    """
        super(QPE, self)
        self._num_qubits = num_qubits
        self.U = unitary

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        qubits = list(qubits)
        yield cirq.H.on_each(*qubits[:-1])
        yield PhaseKickback(self.num_qubits(), self.U)(*qubits)
        yield QFT(self._num_qubits-1)(*qubits[:-1])**-1


class EigenRotation(cirq.Gate):
    """EigenRotation performs the set of rotation on the ancilla qubit 
    equivalent to division on the memory register by each eigenvalue 
    of the matrix. 
    
    The last qubit is the ancilla qubit; all remaining qubits are the register,
    assumed to be big-endian.
    
    It consists of a controlled ancilla qubit rotation for each possible value
    that can be represented by the register. Each rotation is a Ry gate where
    the angle is calculated from the eigenvalue corresponding to the register
    value, up to a normalization factor C.
    """

    def __init__(self, num_qubits, C, t):
        """Initializes an EigenRotation.
        
        Args:
            num_qubits : int
                Number of qubits.
            
            C : float
                Hyperparameter of HHL algorithm.
            
            t : float
                Parameter.
        """
        super(EigenRotation, self)
        self._num_qubits = num_qubits
        self.C = C
        self.t = t
        self.N = 2**(num_qubits-1)

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        for k in range(self.N):
            kGate = self._ancilla_rotation(k)

            # xor's 1 bits correspond to X gate positions.
            xor = k ^ (k-1)

            for q in qubits[-2::-1]:
                # Place X gates
                if xor % 2 == 1:
                    yield cirq.X(q)
                xor >>= 1

                # Build controlled ancilla rotation
                kGate = cirq.ControlledGate(kGate)

            yield kGate(*qubits)

    def _ancilla_rotation(self, k):
        if k == 0:
            k = self.N
        theta = 2*math.asin(self.C * self.N * self.t / (2*math.pi * k))
        return cirq.Ry(theta)

# =============================================================================
# Functions to construct the HHL circuit and simulate it
# =============================================================================

def hhl_circuit(A, C, t, register_size, *input_prep_gates):
    """Constructs the HHL circuit and returns it.
    
    Args:
        A : numpy.ndarray
            Hermitian matrix that defines the system of equations Ax = b.
        
        C : float
            Hyperparameter for HHL.
        
        t : float
            Hyperparameter for HHL
    C and t are tunable parameters for the algorithm.
    register_size is the size of the eigenvalue register.
    input_prep_gates is a list of gates to be applied to |0> to generate the
      desired input state |b>.
    """

    # Ancilla register
    ancilla = cirq.GridQubit(0, 0)
    
    # Work register
    register = [cirq.GridQubit(i + 1, 0) for i in range(register_size)]

    # Input/output register
    memory = cirq.GridQubit(register_size + 1, 0)
    
    # Create a circuit
    circ = cirq.Circuit()
    
    # Unitary e^{iAt} for QPE
    unitary = HamiltonianSimulation(A, t)
    
    # QPE with the unitary e^{iAt}
    qpe = QPE(register_size + 1, unitary)
    
    # Add state preparation circuit for |b>
    circ.append([gate(memory) for gate in input_prep_gates])
    
    # Add the HHL algorithm to the circuit
    circ.append([
        qpe(*(register + [memory])),
        EigenRotation(register_size+1, C, t)(*(register+[ancilla])),
        qpe(*(register + [memory]))**-1,
        cirq.measure(ancilla)
    ])

    # Pauli observable display
    circ.append([
        cirq.pauli_string_expectation(
            cirq.PauliString({ancilla: cirq.Z}),
            key="a"
        ),
        cirq.pauli_string_expectation(
            cirq.PauliString({memory: cirq.X}),
            key="x"
        ),
        cirq.pauli_string_expectation(
            cirq.PauliString({memory: cirq.Y}),
            key="y"
        ),
        cirq.pauli_string_expectation(
            cirq.PauliString({memory: cirq.Z}),
            key="z"
        ),
    ])

    return circ

def expectations(circuit):
    """Simulates the circuit and computes expectation values of the final
    state.
    
    Args:
        circuit : cirq.Circuit
            Circuit to simulate.
    """
    # Get a simulator
    sim = cirq.Simulator()

    ancilla_expectation = 0.0

    # Post-select on the |1> outcome for the ancilla qubit
    # Or equivalently an expectation of -1.0
    while ancilla_expectation != -1.0:
        res = sim.compute_displays(circuit)
        ancilla_expectation = round(res.display_values["a"], 3)

    # Compute expectations and display them
    print("X =", res.display_values["x"])
    print("Y =", res.display_values["y"])
    print("Z =", res.display_values["z"])

# =============================================================================
# Main script
# =============================================================================

def main():
    """Runs the main script of the file."""
    # Constants
    t = 0.358166 * math.pi
    register_size = 4

    # Define the linear system
    A = np.array([[4.30213466-6.01593490e-08j,
                   0.23531802+9.34386156e-01j],
                  [0.23531882-9.34388383e-01j,
                   0.58386534+6.01593489e-08j]])

    # The |b> vector is defined by these gates on the zero state
    # |b> = (0.64510-0.47848j, 0.35490-0.47848j)
    input_prep_gates = [cirq.Rx(1.276359), cirq.Rz(1.276359)]

    # Expected expectation values
    expected = (0.144130 + 0j, 0.413217 + 0j, -0.899154 + 0j)

    # Set C to be the smallest eigenvalue that can be represented by the
    # circuit.
    C = 2*math.pi / (2**register_size * t)

    # Print the actual expectation values
    print("Expected observable outputs:")
    print("X =", expected[0])
    print("Y =", expected[1])
    print("Z =", expected[2])

    # Do the HHL algorithm and print the computed expectation values
    print("\nComputed: ")
    hhlcirc = hhl_circuit(A, C, t, register_size, *input_prep_gates)
    expectations(hhlcirc)

if __name__ == "__main__":
    main()
