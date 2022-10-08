"""Bernstein-Vazirani algorithm in Cirq."""

# Imports
import random

import cirq


def main():
    """Executes the BV algorithm."""
    # Number of qubits
    qubit_count = 8
    
    # Number of times to sample from the circuit
    circuit_sample_count = 3

    # Choose qubits to use
    input_qubits = [cirq.GridQubit(i, 0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count, 0)

    # Pick coefficients for the oracle and create a circuit to query it
    secret_bias_bit = random.randint(0, 1)
    secret_factor_bits = [random.randint(0, 1) for _ in range(qubit_count)]
    oracle = make_oracle(input_qubits,
                         output_qubit,
                         secret_factor_bits,
                         secret_bias_bit)
    print('Secret function:\nf(x) = x*<{}> + {} (mod 2)'.format(
        ', '.join(str(e) for e in secret_factor_bits),
        secret_bias_bit))

    # Embed the oracle into a special quantum circuit querying it exactly once
    circuit = make_bernstein_vazirani_circuit(
        input_qubits, output_qubit, oracle)
    print('\nCircuit:')
    print(circuit)

    # Sample from the circuit a couple times
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=circuit_sample_count)
    frequencies = result.histogram(key='result', fold_func=bitstring)
    print('\nSampled results:\n{}'.format(frequencies))

    # Check if we actually found the secret value.
    most_common_bitstring = frequencies.most_common(1)[0][0]
    print('\nMost common matches secret factors:\n{}'.format(
        most_common_bitstring == bitstring(secret_factor_bits)))


def make_oracle(input_qubits,
                output_qubit,
                secret_factor_bits,
                secret_bias_bit):
    """Gates implementing the function f(a) = a*factors + bias (mod 2)."""
    if secret_bias_bit:
        yield cirq.X(output_qubit)

    for qubit, bit in zip(input_qubits, secret_factor_bits):
        if bit:
            yield cirq.CNOT(qubit, output_qubit)


def make_bernstein_vazirani_circuit(input_qubits, output_qubit, oracle):
    """Solves for factors in f(a) = a*factors + bias (mod 2) with one query."""
    c = cirq.Circuit()
    
    # Initialize qubits
    c.append([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits),
    ])

    # Query oracle
    c.append(oracle)

    # Measure in X basis
    c.append([
        cirq.H.on_each(*input_qubits),
        cirq.measure(*input_qubits, key='result')
    ])

    return c


def bitstring(bits):
    """Creates a bit string out of an iterable of bits."""
    return ''.join(str(int(b)) for b in bits)

if __name__ == '__main__':
    main()
