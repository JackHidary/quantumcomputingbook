"""번스타인-바지라니(Bernstein-Vazirani) 알고리즘 써큐 예제."""

# 가져오기
import random

import cirq


def main():
    """BV알고리즘을 수행합니다."""
    # 입력 큐비트 개수 (역자주 : 총 큐비트 개수는 출력 포함 9개)
    qubit_count = 8
    
    # 회로를 수행하는 횟수
    circuit_sample_count = 3

    # 사용할 큐비트 가져오기.
    input_qubits = [cirq.GridQubit(i, 0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count, 0)

    # 오라클을 위한 계수들을 무작위로 선정하고 질의(query)를 요청할 양자 회로를 생성한다.
    secret_bias_bit = random.randint(0, 1)
    secret_factor_bits = [random.randint(0, 1) for _ in range(qubit_count)]
    oracle = make_oracle(input_qubits,
                         output_qubit,
                         secret_factor_bits,
                         secret_bias_bit)
    print('Secret function:\nf(x) = x*<{}> + {} (mod 2)'.format(
        ', '.join(str(e) for e in secret_factor_bits),
        secret_bias_bit))

    # 양자 오라클을 정확히 한 번만 질의를 요청하는 특수 목적의 양자 회로에 내포한다.
    circuit = make_bernstein_vazirani_circuit(
        input_qubits, output_qubit, oracle)
    print('\n회로 :')
    print(circuit)

    # 회로를 몇 번 측정한다.
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=circuit_sample_count)
    frequencies = result.histogram(key='result', fold_func=bitstring)
    print('\nSampled results:\n{}'.format(frequencies))

    # 실제로 비밀값을 찾아냈는지 확인한다.
    most_common_bitstring = frequencies.most_common(1)[0][0]
    print('\nMost common matches secret factors:\n{}'.format(
        most_common_bitstring == bitstring(secret_factor_bits)))


def make_oracle(input_qubits,
                output_qubit,
                secret_factor_bits,
                secret_bias_bit):
    """함수 f(a) = a*factors + bias (mod 2)를 구현하는 양자 오라클."""
    if secret_bias_bit:
        yield cirq.X(output_qubit)

    for qubit, bit in zip(input_qubits, secret_factor_bits):
        if bit:
            yield cirq.CNOT(qubit, output_qubit)


def make_bernstein_vazirani_circuit(input_qubits, output_qubit, oracle):
    """단 한번의 질의만으로 f(a) = a*factors + bias (mod 2) 문제를 푸는 양자 회로."""
    c = cirq.Circuit()
    
    # 큐비트를 초기화한다.
    c.append([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits),
    ])

    # 양자 오라클에 질의를 요청한다.
    c.append(oracle)

    # X 기저로 측정한다.
    c.append([
        cirq.H.on_each(*input_qubits),
        cirq.measure(*input_qubits, key='result')
    ])

    return c


def bitstring(bits):
    """반복가능한 bits에서 대응되는 비트 문자열을 생성한다."""
    return ''.join(str(int(b)) for b in bits)

if __name__ == '__main__':
    main()
