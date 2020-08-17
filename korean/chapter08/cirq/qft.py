"""4-큐비트계에서 양자 퓨리에 변환을 위한 회로를 생성하기 시뮬레이션하는 예제."""

# 가져오기
import numpy as np

import cirq


def main():
    """양자 퓨리에 변환을 수행합니다."""
    # 회로를 생성하기 화면에 표시합니다.
    qft_circuit = generate_2x2_grid_qft_circuit()
    print('Circuit:')
    print(qft_circuit)

    # 시뮬레이션 한 뒤 최종 양자 상태를 얻습니다.
    simulator = cirq.Simulator()
    result = simulator.simulate(qft_circuit)

    # 최종 상태를 출력합니다.
    print('\nFinalState')
    print(np.around(result.final_state, 3))


def cz_and_swap(q0, q1, rot):
    """입력 큐비트에 제어-Z회전(controlled-RZ)과 교환(SWAP)게이트를 적용하는 생성자. """
    yield cirq.CZ(q0, q1)**rot
    yield cirq.SWAP(q0,q1)


def generate_2x2_grid_qft_circuit():
    """2 x 2 평면 큐비트 구조에 적용되는 양자 퓨리에 변환회로를 반환.

    다음 논문의 회로를 참고: https://arxiv.org/pdf/quant-ph/0402196.pdf.
    """
    # 2*2 정방형 격자 큐비트를 가져온다.
    a, b, c, d = [cirq.GridQubit(0, 0), cirq.GridQubit(0, 1),
                  cirq.GridQubit(1, 1), cirq.GridQubit(1, 0)]

    # 회로를 생성한다.
    circuit = cirq.Circuit(
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cz_and_swap(b, c, 0.25),
        cz_and_swap(c, d, 0.125),
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cz_and_swap(b, c, 0.25),
        cirq.H(a),
        cz_and_swap(a, b, 0.5),
        cirq.H(a),
        strategy=cirq.InsertStrategy.EARLIEST
    )

    return circuit


if __name__ == '__main__':
    main()
