"""벨 부등식 검사를 수행하는 양자 회로를 생성하고 시뮬레이션하기."""

# 라이브러리 가져오기.
import numpy as np

import cirq


def main():
    # 회로 생성.
    circuit = make_bell_test_circuit()
    print('Circuit:')
    print(circuit)

    # 시뮬레이션하기.
    print()
    repetitions = 1000
    print('Simulating {} repetitions...'.format(repetitions))
    result = cirq.Simulator().run(program=circuit,
                                  repetitions=repetitions)

    # 결과들 모으기.
    a = np.array(result.measurements['a'][:, 0])
    b = np.array(result.measurements['b'][:, 0])
    x = np.array(result.measurements['x'][:, 0])
    y = np.array(result.measurements['y'][:, 0])
    
    # 승률 계산하기.
    outcomes = a ^ b == x & y
    win_percent = len([e for e in outcomes if e]) * 100 / repetitions

    # 데이터 출력하기.
    print()
    print('Results')
    print('a:', bitstring(a))
    print('b:', bitstring(b))
    print('x:', bitstring(x))
    print('y:', bitstring(y))
    print('(a XOR b) == (x AND y):\n  ', bitstring(outcomes))
    print('Win rate: {}%'.format(win_percent))


def make_bell_test_circuit():
    # 엘리스(Alice), 밥(Bob)과 심판 큐비트들 선언.
    alice = cirq.GridQubit(0, 0)
    bob = cirq.GridQubit(1, 0)
    alice_referee = cirq.GridQubit(0, 1)
    bob_referee = cirq.GridQubit(1, 1)

    circuit = cirq.Circuit()

    # 엘리스와 밥 사이에 얽힌 양자 상태를 준비하기.
    circuit.append([
        cirq.H(alice),
        cirq.CNOT(alice, bob),
        cirq.X(alice)**-0.25,
    ])

    # 심판 큐비트들은 동전 던지기를 합니다.
    circuit.append([
        cirq.H(alice_referee),
        cirq.H(bob_referee),
    ])

    # 선수들은 심판의 동전 상태에 따라 sqrt(X) 연산을 수행합니다.
    circuit.append([
        cirq.CNOT(alice_referee, alice)**0.5,
        cirq.CNOT(bob_referee, bob)**0.5,
    ])

    # 결과들을 기록합니다.
    circuit.append([
        cirq.measure(alice, key='a'),
        cirq.measure(bob, key='b'),
        cirq.measure(alice_referee, key='x'),
        cirq.measure(bob_referee, key='y'),
    ])

    return circuit


def bitstring(bits):
    return ''.join('1' if e else '_' for e in bits)


if __name__ == '__main__':
    main()
