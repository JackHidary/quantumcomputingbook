"""써큐에서 벨 상태 |\Phi^{+}>를 준비하기 위한 파이썬 스크립트."""

# 써큐 라이브러리를 가져오세요.
import cirq

# 큐비트들과 회로를 준비합니다.
# (역자주: qreg는 quantum register에서 가져온 변수명입니다.)
qreg = [cirq.LineQubit(x) for x in range(2)]
circ = cirq.Circuit()

# 벨 상태를 준비하는 회로를 추가합니다.
circ.append([cirq.H(qreg[0]), 
             cirq.CNOT(qreg[0], qreg[1])])

# 회로를 화면에 표시합니다.
print("Circuit")
print(circ)

# 측정을 모든 큐비트에 추가합니다.
circ.append(cirq.measure(*qreg, key="z"))

# 회로를 시뮬레이션합니다.
sim = cirq.Simulator()
res = sim.run(circ, repetitions=100)

# 측정결과를 출력합니다.
print("\nMeasurements:")
print(res.histogram(key="z"))