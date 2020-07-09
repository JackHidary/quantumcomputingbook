"""파이퀼(pyQuil)에서 QAOA하기 예제"""


##########################################################
# Copyright 2016-2018 Rigetti Computing
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##########################################################

"""
이 예제는 QIP 2018학회에서 Rigetti사의 라이브 프로그래밍 세션에서 실제 선보였던 프로그램입니다.
QAOA의 더 복잡한 구현을 위해서는 그로브 예제와 문서를 찾아주십시오.
http://grove-docs.readthedocs.io/en/latest/qaoa.html
"""

from pyquil import get_qc
from pyquil.quil import Program
from pyquil.gates import H
from pyquil.paulis import sI, sX, sZ, exponentiate_commuting_pauli_sum

# 4-노드 배열 그래프를 생성합니다 : 0-1-2-3.
graph = [(0, 1), (1, 2), (2, 3)]
# 노드들은 [0, 1, 2, 3]입니다.
nodes = range(4)

# 초기 상태 프로그램입니다. 모든 큐비트에 아다마르를 가해 모든 비트열의 중첩을 구합니다.
init_state_prog = Program([H(i) for i in nodes])

# 비용 해밀토니안은 모든 큐비트 쌍 (i, j)에서 0.5 * (1 - \sigma_z^i * \sigma_z^j)의 합.
h_cost = -0.5 * sum(sI(nodes[0]) - sZ(i) * sZ(j) for i, j in graph)

# 구동 해밀토니안은 모든 큐비트 i에 대해 \sigma_x^i의 합.
h_driver = -1. * sum(sX(i) for i in nodes)


def qaoa_ansatz(gammas, betas):
    """
    각도 betas와 gammas의 배열로 주어지는 QAOA 가정법(ansatz) 프로그램을 반환하는 함수.
    차수(order) P인 QAOA program은 len(betas) == len(gammas) == P를 갖는다.
    :param list(float) gammas: 비용 해밀토니안을 매개변수화하는 각도값들의 배열.
    :param list(float) betas: 구동 해밀토니안을 매개변수화하는 각도값들의 배열.
    :return: QAOA 가정법 프로그램.
    :rtype: 프로그램.
    """
    return Program([exponentiate_commuting_pauli_sum(h_cost)(g)
                    + exponentiate_commuting_pauli_sum(h_driver)(b)
                    for g, b in zip(gammas, betas)])


# 상태 초기화 프로그램과 차수 P = 2인 QAOA 가정법 프로그램을 더해 전체 프로그램 생성하기.
program = init_state_prog + qaoa_ansatz([0., 0.5], [0.75, 1.])

# 양자 가상 머신 (QVM)을 초기화하고 프로그램을 수행합니다.
qc = get_qc('9q-generic-qvm')

results = qc.run_and_measure(program, trials=2)

