"""써큐 라이브러리 간단한 예제 프로그램."""

# 써큐 패키지 가져오세요.
import cirq

# 큐비트 하나를 고르세요.
qubit = cirq.GridQubit(0, 0)

# 회로를 만드세요.
circuit = cirq.Circuit([
    cirq.X(qubit),  # 양자 논리에서의 NOT.
    cirq.measure(qubit, key='m')  # 큐비트 측정.
    ]
)

# 회로를 화면에 텍스트로 출력합니다.
print("Circuit:")
print(circuit)

# 회로를 실행하기 위한 시뮬레이터를 가져옵니다.
simulator = cirq.Simulator()

# 회로를 여러번 시뮬레이션 하세요.
result = simulator.run(circuit, repetitions=10)

# 결과를 출력합니다.
print("Results:")
print(result)
