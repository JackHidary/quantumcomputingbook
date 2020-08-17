"""키스킷 초고밀집 부호."""

# 가져오기.
import qiskit

# 2개 큐비트의 양자 레지스터와 2개 비트의 고전레지스터로 회로 구성하기.
qreg = qiskit.QuantumRegister(2)
creg = qiskit.ClassicalRegister(2)
circ = qiskit.QuantumCircuit(qreg, creg)

# 아다마르(Hadamard) 게이트를 0번째 큐비트에 적용하여 중첩상태를 구현합니다.
circ.h(qreg[0])

# X 연산자를 0번째 큐비트에 적용합니다.
circ.x(qreg[0])

# 벨상태를 얻기 위해 0번째와 1번째 큐비트로 CNOT연산을 가합니다.
# (역자주: 첫 번째 인자가 제어비트, 두 번째 인자가 피연산비트입니다.)
circ.cx(qreg[0], qreg[1])

# 아다마르 연산자를 0번째 큐비트에 적용하여 중첩을 해제합니다.
circ.h(qreg[0])

# 메시지를 얻기위해 측정 게이트를 추가합니다.
circ.measure(qreg, creg)

# 회로를 출력합니다.
print("Circuit:")
print(circ.draw())

# 상태벡터 시뮬레이터 백엔드 위에서 회로를 실행하고 결과를 얻습니다.
backend = qiskit.Aer.get_backend("statevector_simulator")
job = qiskit.execute(circ, backend)
res = job.result()
print(res.get_counts())
