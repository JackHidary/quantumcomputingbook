"""키스킷에서 양자 원격이동하기."""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
#from qiskit import available_backends, execute

# 양자 레지스터와 고전 레지스터를 생성합니다.
q = QuantumRegister(3)
c = ClassicalRegister(3)
qc = QuantumCircuit(q, c)

# 초기 중첩 양자 상태 |+>를 구현합니다.
qc.h(q[0])

# 큐비트를 중첩 해제합니다.
qc.h(q[0])

# CNOT 연산자를 적용합니다.
qc.cx(q[0], q[1])

# 큐비트들을 중첩상태로 놓습니다. 현재 두 상태는 같습니다.
qc.h(q[0])
qc.h(q[1])

# 큐비트 0에 대해 단일 유니타리 연산으로 초기 상태를 준비합니다.
qc.u1(0.5, q[0])

# CNOT 연산을 큐비트 0과 큐비트 1에 적용합니다.
qc.cx(q[0], q[1])

# 큐비트 0을 |+>와 |-> 기저로 측정합니다.
qc.h(q[0])
qc.measure(q[0], c[0])

# 필요하다면 큐비트 1에 대해 위상 보정(phase correction)을 수행합니다.
if c[0] == 1:
   qc.z(q[1])

# 큐비트 0에 대해 단일 유니타리 연산으로 초기 상태를 준비합니다.
qc.u1(0.5, q[0])

# 큐비트 1과 큐비트 2를 사용해 얽힌 상태를 만듭니다.
qc.h(q[1])
qc.cx(q[1], q[2])

# 최적화를 위해 게이트를 재배열하는 것을 막고자 장막(Barrier)을 걸어둡니다.
qc.barrier(q)

# CNOT 연산을 큐비트 0과 큐비트 1에 적용합니다.
qc.cx(q[0], q[1])

# 큐비트 1을 계산기저에서 측정합니다.
qc.measure(q[1], c[1])
# 필요하다면 큐비트 2에 대해서 비트 반전 보정(bit flip correction)을 수행합니다.
if c[1] == 1:
    qc.x(q[2])
 
# 큐비트 0을 |+>와 |-> 기저로 측정합니다.
qc.h(q[0])
qc.measure(q[0], c[0])
# 필요하다면 큐비트 2에 대해 위상 보정(phase correction)을 수행합니다.
if c[0] == 1:
    qc.z(q[2])

print(qc.draw())