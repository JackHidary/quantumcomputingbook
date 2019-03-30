"""Creates and simulates a circuit for Quantum Fourier Transform (QFT)
on a 4 qubit system.
"""

# Imports
import numpy as np

import cirq


def main():
    """Demonstrates the Quantum Fourier transform."""
    # Create circuit and display it
    qft_circuit = generate_2x2_grid_qft_circuit()
    print('Circuit:')
    print(qft_circuit)
    
    # Simulate and collect the final state
    simulator = cirq.google.XmonSimulator()
    result = simulator.simulate(qft_circuit)
    
    # Display the final state
    print('\nFinalState')
    print(np.around(result.final_state, 3))


def cz_and_swap(q0, q1, rot):
    """Yields a controlled-RZ gate and SWAP gate on the input qubits."""
    yield cirq.CZ(q0, q1)**rot
    yield cirq.SWAP(q0,q1)


def generate_2x2_grid_qft_circuit():
    """Returns a QFT circuit on a 2 x 2 planar qubit architecture.
     
    Circuit adopted from https://arxiv.org/pdf/quant-ph/0402196.pdf.
    """
    # Define a 2*2 square grid of qubits
    a, b, c, d = [cirq.GridQubit(0, 0), cirq.GridQubit(0, 1),
                  cirq.GridQubit(1, 1), cirq.GridQubit(1, 0)]

    # Create the Circuit
    circuit = cirq.Circuit.from_ops(
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cz_and_swap(b, c, 0.25),
        cz_and_swap(c, d, 0.125),
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cz_and_swap(b, c, 0.25),
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cirq.H(a),
        strategy=cirq.InsertStrategy.EARLIEST
    )
    
    return circuit


if __name__ == '__main__':
    main()
