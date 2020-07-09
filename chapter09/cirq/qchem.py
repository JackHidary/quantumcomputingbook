"""오픈페르미온(OpenFermion)과 써큐를 사용한 양자 화학 계산 예제.

Requirements:
cirq==0.7.0
openfermion==0.11.0
openfermioncirq==0.4.0
"""

# 가져오기
import numpy
import scipy
import sympy

import cirq
import openfermion
import openfermioncirq

# 큐비트 개수와 시뮬레이션 시간, 그리고 실험 재현을 위한 난수 씨앗값 설정.
n_qubits = 3
simulation_time = 1.0
random_seed = 8317

# 무작위 1-체 연산자 생성.
T = openfermion.random_hermitian_matrix(n_qubits, seed=random_seed)
print("Hamiltonian:", T, sep="\n")

# 오픈페르미온의 "FermionOperator" 형태의 해밀토니안을 계산하기.
H = openfermion.FermionOperator()
for p in range(n_qubits):
    for q in range(n_qubits):
        term = ((p, 1), (q, 0))
        H += openfermion.FermionOperator(term, T[p, q])
print("\nFermion operator:")
print(H)

# Diagonalize T를 대각화 하고 ("u"로 알려진) 기저 변환 행렬 구하기.
eigenvalues, eigenvectors = numpy.linalg.eigh(T)
basis_transformation_matrix = eigenvectors.transpose()

# 큐비트 레지스터 초기화하기.
qubits = cirq.LineQubit.range(n_qubits)

# 고유기저로 회전하기.
inverse_basis_rotation = cirq.inverse(
    openfermioncirq.bogoliubov_transform(qubits, basis_transformation_matrix)
)
circuit = cirq.Circuit.from_ops(inverse_basis_rotation)

# 회로에 대각 위상 회전을 추가하기.
for k, eigenvalue in enumerate(eigenvalues):
    phase = -eigenvalue * simulation_time
    circuit.append(cirq.Rz(rads=phase).on(qubits[k]))

# 마지막으로, 다시 계산 기저로 돌아오기.
basis_rotation = openfermioncirq.bogoliubov_transform(
    qubits, basis_transformation_matrix
)
circuit.append(basis_rotation)

# 무작위로 initial_state를 초기화하기.
initial_state = openfermion.haar_random_vector(
    2 ** n_qubits, random_seed).astype(numpy.complex64)

# 회로의 정확한 출력을 수치적으로 계산하기.
hamiltonian_sparse = openfermion.get_sparse_operator(H)
exact_state = scipy.sparse.linalg.expm_multiply(
    -1j * simulation_time * hamiltonian_sparse, initial_state
)

# Cirq의 시뮬레이터를 사용하여 회로를 출력상태 계산하기.
simulator = cirq.Simulator()
result = simulator.simulate(circuit, qubit_order=qubits,
                            initial_state=initial_state)
simulated_state = result.final_state

# 마지막 충실도(fidelity) 를 출력하기
fidelity = abs(numpy.dot(simulated_state, numpy.conjugate(exact_state)))**2
print("\nfidelity =", round(fidelity, 4))
