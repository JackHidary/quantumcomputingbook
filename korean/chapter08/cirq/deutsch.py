"""도이치-조사(Deutsch-Jozsa) 알고리즘."""

# 써큐 라이브러리를 가져온다.
import cirq

# 데이터 큐비트와 목적 큐비트 두 개의 큐비트를 가져온다.
q0, q1 = cirq.LineQubit.range(2)

# 양자 오라클 사전을 정의한다.
oracles = {'0': [], '1': [cirq.X(q1)], 'x': [cirq.CNOT(q0, q1)],
           'notx': [cirq.CNOT(q0, q1), cirq.X(q1)]}

def deutsch_algorithm(oracle):
    """주어진 양자 오라클 oracle을 기반으로 도이치 알고리즘을 수행하는 양자회로의 생성자."""
    yield cirq.X(q1)
    yield cirq.H(q0), cirq.H(q1)
    yield oracle
    yield cirq.H(q0)
    yield cirq.measure(q0)

# 모든 오라클에 대한 양자 회로들을 화면에 출력하기.
for key, oracle in oracles.items():
    print('Circuit for {}...'.format(key))
    print(cirq.Circuit(deutsch_algorithm(oracle)), end="\n\n")

# 시뮬레이터 가져오기.
simulator = cirq.Simulator()

# 상수함수와 균형함수를 구분하기 위해 각각의 오라클에 대한 회로를 수행한다.
for key, oracle in oracles.items():
    result = simulator.run(
        cirq.Circuit(deutsch_algorithm(oracle)),
        repetitions=10
    )
    print('oracle: {:<4} results: {}'.format(key, result))
