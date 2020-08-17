"""써큐에서 양자 위상 추정(QPE)하기."""

# 가져오기
import numpy as np
from scipy.stats import unitary_group

import cirq

# =============================================================================
# 보조함수
# =============================================================================

def binary_decimal(string):
    """0babc...의 수치값을 반환합니다. 이때 a, b, c, ... 는 각각 0 또는 1입니다.
       (역자주: 0x1F가 16진수 1F를 의미하듯, 0babc도 2진수 abc를 의미합니다.)
    
    Examples:
        0b10 --> 0.5
        0b01 --> 0.25
    """
    val = 0.0
    for (ind, bit) in enumerate(string[2:]):
        if int(bit) == 1:
            val += 2**(-1 -ind)
    return val

# =============================================================================
# QPE 입력
# =============================================================================

# 결과 재현을 위한 씨앗값 설정.
np.random.seed(123)

# 두 개 큐비트들에 대한 무작위 유니타리 행렬을 생성.
m = 2
dim = 2**m
unitary = unitary_group.rvs(dim)

unitary = np.identity(4)

xmat = np.array([[0, 1], [1, 0]])
zmat = np.array([[1, 0], [0, -1]])
unitary = np.kron(xmat, zmat)

# 콘솔 화면에 출력하기
print("Unitary:")
print(unitary)

# 행렬을 고전적으로 대각화하기.
evals, evecs = np.linalg.eig(unitary)

# =============================================================================
# QPE를 위한 회로 만들기.
# =============================================================================

# readout/answer 레지스터에 들어갈 큐비트 개수 설정하기 (정밀도는 비트 개수에 비례합니다.)
n = 8

# 출력 레지스터
regA = cirq.LineQubit.range(n)

# 고유상태를 저장하기위한 레지스터.
regB = cirq.LineQubit.range(n, n + m)

# 회로 얻기
circ = cirq.Circuit()

# 모든 출력 레지스터 큐비트에 아다마르 연산자를 가하기.
circ.append(cirq.H.on_each(regA))

# 두번쨰 레지스터의 모든 큐비트에 아다마르 연산자 가하기.
#circ.append(cirq.H.on_each(regB))

# 입력 유니타리 행렬로 써큐 게이트 만들기
ugate = cirq.ops.matrix_gates.TwoQubitMatrixGate(unitary)

# 위 유니타리 게이트의 제어 버전 만들기
cugate = cirq.ops.ControlledGate(ugate)

# 제어-U^{2^k} 연산들을 만들기.
for k in range(n):
    circ.append(cugate(regA[k], *regB)**(2**k))

# 역 QFT 수행.
for k in range(n - 1):
    circ.append(cirq.H.on(regA[k]))
    targ = k + 1
    for j in range(targ):
        exp = -2**(j - targ)
        rot = cirq.Rz(exp)
        crot = cirq.ControlledGate(rot)
        circ.append(crot(regA[j], regA[targ]))
circ.append(cirq.H.on(regA[n - 1]))

"""
# 이것이 바로 QFT입니다!
for k in reversed(range(n)):
    circ.append(cirq.H.on(regA[k]))
    for j in reversed(range(k)):
        exp = 2**(j - k)
        rot = cirq.Rz(exp)
        crot = cirq.ControlledGate(rot)
        circ.append(crot(regA[j], regA[k]))
"""

# 출력 레지스터에서 모든 큐비트를 측정하기.
circ.append(cirq.measure(*regA, key="z"))

# 회로를 출력합니다.
#print("Circuit:")
#print(circ[5:])

# =============================================================================
# QPE 회로 실행하기
# =============================================================================

sim = cirq.Simulator()

res = sim.run(circ, repetitions=1000)

hist = res.histogram(key="z")

top = hist.most_common(2)

estimated = [np.exp(2j * np.pi * binary_decimal(bin(x[0]))) for x in top]

print("\nEigenvalues from QPE:")
print(sorted(estimated, key=lambda x: abs(x)**2))

print("\nActual eigenvalues:")
print(sorted(evals, key=lambda x: abs(x)**2))
