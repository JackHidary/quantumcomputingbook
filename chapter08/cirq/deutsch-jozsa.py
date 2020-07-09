"""3 큐비트 도이치-조사(Deutsch-Jozsa) 알고리즘의 써큐 예제."""

# 써큐 라이브러리 가져오기.
import cirq

# 2개 데이터와 1개 목적 큐비트, 총 3개 큐비트 가져오기.
q0, q1, q2 = cirq.LineQubit.range(3)

# 상수함수를 위한 양자 오라클 게이트 집합 정의.
constant = ([], [cirq.X(q2)])

# 균형함수를 위한 양자 오라클 게이트 집합 정의.
balanced = ([cirq.CNOT(q0, q2)],
            [cirq.CNOT(q1, q2)],
            [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2)],
            [cirq.CNOT(q0, q2), cirq.X(q2)],
            [cirq.CNOT(q1, q2), cirq.X(q2)],
            [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2), cirq.X(q2)])

def your_circuit(oracle):
    """3개 큐비트 도이치-조사 알고리즘을 위한 양자 회로 생성자."""
    # 위상 반동(phase kickback) 공식을 사용합니다.
    yield cirq.X(q2), cirq.H(q2)

    # 입력 비트들을 동등한 양자 중첩상태로 바꿉니다.
    yield cirq.H(q0), cirq.H(q1)

    # 함수에 질의를 요청합니다.
    yield oracle

    # 결과를 얻기 위해 간섭을 수행하고 마지막 큐비트를 |1> 상태로 둡니다.
    yield cirq.H(q0), cirq.H(q1), cirq.H(q2)

    # 결과를 목적 큐비트에 담기 위해 마지막 OR 게이트를 수행합니다.
    yield cirq.X(q0), cirq.X(q1), cirq.CCX(q0, q1, q2)
    yield cirq.measure(q2)

# 시뮬레이터를 가져옵니다.
simulator = cirq.Simulator()

# 상수 함수 오라클을 위한 양자 회로를 수행합니다.
print('Your result on constant functions')
for oracle in constant:
    result = simulator.run(cirq.Circuit(your_circuit(oracle)), repetitions=10)
    print(result)

# 균형 함수 오라클을 위한 양자 회로를 수행합니다.
print('Your result on balanced functions')
for oracle in balanced:
    result = simulator.run(cirq.Circuit(your_circuit(oracle)), repetitions=10)
    print(result)
