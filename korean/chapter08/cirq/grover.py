"""써큐 그로버(Grover) 알고리즘."""

# 가져오기
import random

import cirq


def set_io_qubits(qubit_count):
    """qubit_count개의 입력 큐비트와 1개의 출력 큐비트를 반환합니다."""
    input_qubits = [cirq.GridQubit(i, 0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count, 0)
    return (input_qubits, output_qubit)


def make_oracle(input_qubits, output_qubit, x_bits):
    """함수 {f(x) = 1 if x==x', f(x) = 0 if x!= x'}를 구현합니다."""
    # 양자 오라클을 생성합니다.
    # 입력 큐비트와 입력 x 비트가 (1, 1)인 경우 토폴리(Toffoli)게이트 입니다.
    # 그외의 모든 경우는 0 비트를 반전합니다.
    yield(cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)
    yield(cirq.TOFFOLI(input_qubits[0], input_qubits[1], output_qubit))
    yield(cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)


def make_grover_circuit(input_qubits, output_qubit, oracle):
    """sqrt(N)번 양자 오라클을 수행하여 얻은 상태에서 값을 추출합니다."""
    # 2개 입력 큐비트의 경우 그로버 연선자를 단 한번만 수행합니다.
    c = cirq.Circuit()

    # 큐비트를 초기화합니다.
    c.append([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits),
    ])

    # 양자 오라클에 질의합니다.
    c.append(oracle)

    # 그로버 연산자를 구축합니다.
    c.append(cirq.H.on_each(*input_qubits))
    c.append(cirq.X.on_each(*input_qubits))
    c.append(cirq.H.on(input_qubits[1]))
    c.append(cirq.CNOT(input_qubits[0], input_qubits[1]))
    c.append(cirq.H.on(input_qubits[1]))
    c.append(cirq.X.on_each(*input_qubits))
    c.append(cirq.H.on_each(*input_qubits))

    # 결과를 측정합니다.
    c.append(cirq.measure(*input_qubits, key='result'))

    return c


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)


def main():
    qubit_count = 2
    circuit_sample_count = 10

    # 입출력 큐비트를 설정합니다.
    (input_qubits, output_qubit) = set_io_qubits(qubit_count)

    # 양자 오라클에 요청하기 위한 비밀값 비트열 x를 생성합니다.
    x_bits = [random.randint(0, 1) for _ in range(qubit_count)]
    print('Secret bit sequence: {}'.format(x_bits))

    # 블랙박스 양자 오라클을 생성합니다.
    oracle = make_oracle(input_qubits, output_qubit, x_bits)

    # 생성된 오라클을 내포하는 그로버 알고리즘 양자 회로를 생성합니다.
    circuit = make_grover_circuit(input_qubits, output_qubit, oracle)
    print('Circuit:')
    print(circuit)

    # 양자 회로를 수행합니다.
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=circuit_sample_count)

    frequencies = result.histogram(key='result', fold_func=bitstring)
    print('Sampled results:\n{}'.format(frequencies))

    # 실제로 목표로한 비밀값을 찾아냈는지 확인합니다.
    most_common_bitstring = frequencies.most_common(1)[0][0]
    print('Most common bitstring: {}'.format(most_common_bitstring))
    print('Found a match: {}'.format(
        most_common_bitstring == bitstring(x_bits)))


if __name__ == '__main__':
    main()
    
