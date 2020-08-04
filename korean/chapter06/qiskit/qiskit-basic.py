"""키스킷 간단한 예제 프로그램."""

# 키스킷 패키지를 가져오세요.
import qiskit

# 1개 큐비트를 갖는 양자 레지스터를 생성하세요.
qreg = qiskit.QuantumRegister(1, name='qreg')

# 1개 큐비트와 연결된 고전 레지스터를 생성하세요.
creg = qiskit.ClassicalRegister(1, name='creg')

# 위의 두 레지스터들로 구성된 양자 회로를 생성하세요.
circ = qiskit.QuantumCircuit(qreg, creg)

# NOT연산을 추가하세요.
circ.x(qreg[0])

# 측정하기를 추가하세요.
circ.measure(qreg, creg)

# 회로를 출력합니다.
print(circ.draw())

# 양자 회로를 실행할 시뮬레이터 백엔드를 가져옵니다.
backend = qiskit.BasicAer.get_backend("qasm_simulator")

# 회로를 가져온 백엔드 위에서 실행하고 측정결과를 얻습니다.
job = qiskit.execute(circ, backend, shots=10)
result = job.result()

# 측정결과를 출력합니다.
print(result.get_counts())
