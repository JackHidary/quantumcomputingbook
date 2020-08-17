"""써큐 초고밀집 부호(superdense coding) 예제 프로그램."""

# 라이브러리 가져오기
import cirq

# 출력결과를 보여주기 위한 보조 함수.
def bitstring(bits):
    return ''.join('1' if e else '0' for e in bits)

# 큐비트 두 개와 양자 회로를 생성합니다.
qreg = [cirq.LineQubit(x) for x in range(2)]
circ = cirq.Circuit()

# 각 메시지별 연산들의 사전을 정의합니다.
message = {"00": [],
           "01": [cirq.X(qreg[0])],
           "10": [cirq.Z(qreg[0])],
           "11": [cirq.X(qreg[0]), cirq.Z(qreg[0])]}

# 엘리스(Alice)가 벨 상태를 생성합니다.
circ.append(cirq.H(qreg[0]))
circ.append(cirq.CNOT(qreg[0], qreg[1]))

# 엘리스가 보낼 메시지를 선택합니다.
m = "01"
print("Alice's sent message =", m)

# 엘리스가 보낼 메시지를 적절한 양자 연산자들로 부호화합니다.
circ.append(message[m])

# 밥(Bob)이 벨 기저에서 측정합니다.
circ.append(cirq.CNOT(qreg[0], qreg[1]))
circ.append(cirq.H(qreg[0]))
circ.append([cirq.measure(qreg[0]), cirq.measure(qreg[1])])

# 전체 회로를 출력합니다.
print("\nCircuit:")
print(circ)

# 시뮬레이터 백엔드에서 양자회로를 실행합니다.
sim = cirq.Simulator()
res = sim.run(circ, repetitions=1)

# 회로의 측정 결과인 밥이 받은 메시지를 출력합니다.
print("\nBob's received message =", bitstring(res.measurements.values()))
