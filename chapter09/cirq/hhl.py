"""
선형 연립방정식을 풀기 위한 해로우(Harrow), 하시딤(Hassidim), 로이드(Lloyd)의 HHL 알고리즘

HHL 알고리즘은 선형 연립 방정식을 푸는 알고리즘으로, 특히 Ax = b인 등식에서 행렬 A가 에르미트
행렬이고 벡터 b가 주어졌을 때 벡터 x를 찾는 문제를 위한 알고리즘입니다. 양자 시스템에서 이 문제를
해결할 때, 반드시 벡터 b는 크기가 1인 단위벡터여야 합니다. 그럼 수식은 다음과 같이 됩니다:

|x> = A**-1 |b> / || A**-1 |b> ||

이 알고리즘은 다음 3개의 큐비트 집합을 사용합니다. 1. 단일 보조 큐비트, 2. (행렬 A의 고유값을
저장할) 레지스터, 그리고 3. (|b>와 |x>를 저장할) 메모리 큐비트들입니다.
이제 알고리즘은 다음 순서대로 진행됩니다.:
1) 행렬 A의 고유값을 추출하기 위한 양자 위상 추정
2) 보조 큐비트의 제어 회전
3) 역 양자 위상 추정으로 가역계산 수행.

알고리즘의 자세한 설명을 위해서는 아래 참조에 있는 논문들을 참고해주십시오.
우리는 HHL 논문에서 정의된 변수들을 이용해 알고리즘을 설명할 것입니다.

이 예제는 임의의 2x2 에르미트 행렬의 HHL 알고리즘을 구현합니다. 알고리즘은 |x> 상태의 파울리
측정의 기대값을 출력합니다. 결과의 정확도는 다음 요인들에 의해 결정됨을 참고해주십시오:
* 레지스터의 크기
* 매개변수 C와 t의 선택.

결과가 오류없이 완벽히 구해지는 조건들은 다음과 같습니다.
* 만일 행렬의 각 고유값이 다음의 형태

  2π/t * k/N,

  0≤k<N이고 N=2^n이며 n이 레지스터 크기인 경우입니다. 다시 말하면 k가 정확히 그 레지스터로
  표현이 가능한 수여야 합니다.
* C ≤ 2π/t * 1/N로, 최소 고유값이 회로에 저장될 수 있어야 합니다.

혹은 레지스터 크기가 충분히 커서 모든 고유값쌍의 비율이 가능한 레지스터 값들로 근사가 잘 될 때
결과가 좋게 나옵니다. 가능한 레지스터 값과 그 값에 대응되는 고유값으로부터 얻어지는 비례인자를
s로 정의합니다. 그렇다면 매개변수 t를 결정하는 한 가지 방법으로 다음이 있을 수 있습니다.

t = 2π/sN

임의의 행렬에 대하여, 고유값들의 성질이 알려져 있지 않기 떄문에 행렬의 조건수에 따라 C와 t가
미세조정됩니다.


=== 참  조 ===
Harrow, Aram W. et al. Quantum algorithm for solving linear systems of
equations (the HHL paper)
https://arxiv.org/abs/0811.3171

Coles, Eidenbenz et al. Quantum Algorithm Implementations for Beginners
https://arxiv.org/abs/1804.03719

=== 회  로  ===
2개 레지스터 큐비트 회로의 예제.

(0, 0): ─────────────────────────Ry(θ₄)─Ry(θ₁)─Ry(θ₂)─Ry(θ₃)──────────────M──
                     ┌──────┐    │      │      │      │ ┌───┐
(1, 0): ─H─@─────────│      │──X─@──────@────X─@──────@─│   │─────────@─H────
           │         │QFT^-1│    │      │      │      │ │QFT│         │
(2, 0): ─H─┼─────@───│      │──X─@────X─@────X─@────X─@─│   │─@───────┼─H────
           │     │   └──────┘                           └───┘ │       │
(3, 0): ───e^iAt─e^2iAt───────────────────────────────────────e^-2iAt─e^-iAt─

참고: 위 회로도의 QFT는 마지막 교환연산자들을 생략했는데, 이는 위상 반동을 위한 큐비트 순서
반전에 의해 암묵적으로 포함됩니다.
"""

import math
import numpy as np
import sympy
import cirq


class PhaseEstimation(cirq.Gate):
    """
    양자 위상 추정을 위한 게이트.

    추정할 위상을 지닌 유니타리 게이트 unitary를 입력받습니다.
    마지막 큐비트가 고유벡터를 저장합니다;다른 모든 큐비트들은 추정된 위상을
    빅엔디안(big-endian)으로 저장합니다.
    """

    def __init__(self, num_qubits, unitary):
        self._num_qubits = num_qubits
        self.U = unitary

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        qubits = list(qubits)
        yield cirq.H.on_each(*qubits[:-1])
        yield PhaseKickback(self.num_qubits(), self.U)(*qubits)
        yield cirq.QFT(*qubits[:-1], without_reverse=True)**-1


class HamiltonianSimulation(cirq.EigenGate, cirq.SingleQubitGate):
    """
    행렬의 지수화 e^iAt를 표현하는 게이트

    이 게이트는 EigenGate와 np.linalg.eigh()를 합한 구현으로 여기서는 순수하게 시연목적으로
    사용됩니다. 만일 큰 행렬이 사용된다면, 예를들어 써큐의 선형 연산자들을 사용하여 실제
    해밀토니안 시뮬레이션를 위한 회로를 구현해야 합니다.
    """

    def __init__(self, A, t, exponent=1.0):
        cirq.SingleQubitGate.__init__(self)
        cirq.EigenGate.__init__(self, exponent=exponent)
        self.A = A
        self.t = t
        ws, vs = np.linalg.eigh(A)
        self.eigen_components = []
        for w, v in zip(ws, vs.T):
            theta = w*t / math.pi
            P = np.outer(v, np.conj(v))
            self.eigen_components.append((theta, P))

    def _with_exponent(self, exponent):
        return HamiltonianSimulation(self.A, self.t, exponent)

    def _eigen_components(self):
        return self.eigen_components


class PhaseKickback(cirq.Gate):
    """
    양자 위상 추정의 위상 반동 단계에서 사용되는 게이트.

    메모리 큐비트를 목적으로 하고 각 레지스터 큐비트를 제어로 하여 연속된 제어 e^iAt 게이트들을
    구현합니다. 이때 큐비트의 첨자를 기준으로 2의 거듭제곱으로 표현됩니다.
    위상 추정할 유니타리 게이트 unitary를 입력받습니다.
    """

    def __init__(self, num_qubits, unitary):
        super(PhaseKickback, self)
        self._num_qubits = num_qubits
        self.U = unitary

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        qubits = list(qubits)
        memory = qubits.pop()
        for i, qubit in enumerate(qubits):
            yield cirq.ControlledGate(self.U**(2**i))(qubit, memory)


class EigenRotation(cirq.Gate):
    """
    EigenRotation은 보조 큐비트 상에서 회전연산을 수행합니다. 이는 메모리 레지스터 상에서
    행렬의 각 고유값으로 나누는 연산과 동일합니다. 마지막 큐비트는 보조 큐비트입니다;
    나머지 모든 큐비트들은 레지스터로 빅엔디안으로 가정합니다.

    이는 레지스터에서 표현가능한 각 값들을 위한 제어 보조 큐비트 회전으로 이루어 졌습니다.
    각 회전은 Ry게이트로 회전각은 레지스터 값에 대응되는 고유값으로 계산됩니다.
    최대 정규화 상수 C이내로 차이가 납니다.
    """

    def __init__(self, num_qubits, C, t):
        super(EigenRotation, self)
        self._num_qubits = num_qubits
        self.C = C
        self.t = t
        self.N = 2**(num_qubits-1)

    def num_qubits(self):
        return self._num_qubits

    def _decompose_(self, qubits):
        for k in range(self.N):
            kGate = self._ancilla_rotation(k)

            # xor 변수의 1 비트의 위치는 X 게이트 위치에 대응됩니다.
            xor = k ^ (k-1)

            for q in qubits[-2::-1]:
                # X 게이트를 가합니다.
                if xor % 2 == 1:
                    yield cirq.X(q)
                xor >>= 1

                # 제어 보조 회전을 구성합니다.
                kGate = cirq.ControlledGate(kGate)

            yield kGate(*qubits)

    def _ancilla_rotation(self, k):
        if k == 0:
            k = self.N
        theta = 2*math.asin(self.C * self.N * self.t / (2*math.pi * k))
        return cirq.Ry(theta)


def hhl_circuit(A, C, t, register_size, *input_prep_gates):
    """
    HHL 회로를 구성합니다.

    Args:
        A: 에르미트 행렬.
        C: 알고리즘 매개변수, 위 설명 참고.
        t: 알고리즘 매개변수, 위 설명 참고.
        register_size: 고유값 레지스터의 크기.
        memory_basis: 'x', 'y', 'z' 중 하나로 메모리 큐비트를 측정할 기저.
        input_prep_gates: |0> 상태에 가할 게이트들의 리스트로 원하는 입력 상태 |b>에 해당.

    Returns:
        HHL 회로를 반환. 보조 큐비트 측정은 키값 'a'를, 메모리 큐비트의 측정은 키값 'm'을
        갖습니다. 회로에는 두 가지 매개변수가 있습니다. `exponent`와 `phase_exponent`는
        메모리에 대한 측정이 이루어지기 전에 `cirq.PhasedXPowGate`로 가해질 가능한 회전에
        대응됩니다.
    """

    ancilla = cirq.LineQubit(0)
    # 행렬의 고유값을 저장하기 위한 레지스터.
    register = [cirq.LineQubit(i + 1) for i in range(register_size)]
    # 입력과 출력 벡터를 저장하기 위한 메모리 큐비트.
    memory = cirq.LineQubit(register_size + 1)

    c = cirq.Circuit()
    hs = HamiltonianSimulation(A, t)
    pe = PhaseEstimation(register_size+1, hs)
    c.append([gate(memory) for gate in input_prep_gates])
    c.append([
        pe(*(register + [memory])),
        EigenRotation(register_size + 1, C, t)(*(register + [ancilla])),
        pe(*(register + [memory]))**-1,
        cirq.measure(ancilla, key='a')
    ])

    c.append([
        cirq.PhasedXPowGate(
            exponent=sympy.Symbol('exponent'),
            phase_exponent=sympy.Symbol('phase_exponent'))(memory),
        cirq.measure(memory, key='m')
    ])

    return c


def simulate(circuit):
    simulator = cirq.Simulator()

    # 메모리 큐비트의 X, Y, Z 기저를 각각을 측정하기 위한 회전 게이트용 매개변수들.
    params = [{
        'exponent': 0.5,
        'phase_exponent': -0.5
    }, {
        'exponent': 0.5,
        'phase_exponent': 0
    }, {
        'exponent': 0,
        'phase_exponent': 0
    }]

    results = simulator.run_sweep(circuit, params, repetitions=5000)

    for label, result in zip(('X', 'Y', 'Z'), list(results)):
        # 오직 보조 큐비트가 1인 경우만 선택합니다.
        # TODO 진폭 증폭 알고리즘을 사용하여 최적화히기
        expectation = 1 - 2 * np.mean(
            result.measurements['m'][result.measurements['a'] == 1])
        print('{} = {}'.format(label, expectation))


def main():
    """
    HHL을 행렬 입력과 결과 큐비트 상태인 |x>의 파울리 측정 출력을 시뮬레이션하기.
    기대되는 해 |x>로 부터 기대되는 관측량을 계산합니다.
    """

    # 고유값분해 결과:
    # >>> import numpy as np
    # >>> x, y = np.linalg.eig(A)
    # >>> [z for z in zip(list(x.astype(np.float32)), list(y))]
    # [(4.537, array([ 0.9715551 +0.j        , -0.05783371-0.22964251j])),
    #  (0.349, array([0.05783391-0.22964302j, 0.97155524+0.j        ]))]
    # |b> = (0.64510-0.47848j, 0.35490-0.47848j)
    # |x> = (-0.0662724-0.214548j, 0.784392-0.578192j)
    A = np.array([[4.30213466-6.01593490e-08j,
                   0.23531802+9.34386156e-01j],
                  [0.23531882-9.34388383e-01j,
                   0.58386534+6.01593489e-08j]])
    t = 0.358166*math.pi
    register_size = 4
    input_prep_gates = [cirq.Rx(1.276359), cirq.Rz(1.276359)]
    expected = (0.144130, 0.413217, -0.899154)

    # C를 회로에서 표현가능한 최소의 고유값에 맞춥니다.
    C = 2*math.pi / (2**register_size * t)

    # 회로를 시뮬레이션합니다.
    print("Expected observable outputs:")
    print("X =", expected[0])
    print("Y =", expected[1])
    print("Z =", expected[2])
    print("Actual: ")
    simulate(hhl_circuit(A, C, t, register_size, *input_prep_gates))


if __name__ == '__main__':
    main()
