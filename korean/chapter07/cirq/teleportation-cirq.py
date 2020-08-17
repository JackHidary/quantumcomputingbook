"""써큐에서 양자 원격이동하기. 다음 예제에서 수정되었습니다.:

https://github.com/quantumlib/Cirq/blob/master/examples/quantum_teleportation.py
"""

# 가져오기.
import random

import cirq


def make_quantum_teleportation_circuit(ranX, ranY):
    """양자 원격이동 회로를 반환합니다."""
    circuit = cirq.Circuit()
    msg, alice, bob = cirq.LineQubit.range(3)

    # 엘리스(Alice)와 밥(Bob)이 공유할 벨상태를 생성합니다.
    circuit.append([cirq.H(alice), cirq.CNOT(alice, bob)])

    # 보낼 메시지를 위한 무작위 상태를 생성합니다.
    circuit.append([cirq.X(msg)**ranX, cirq.Y(msg)**ranY])

    # 엘리스의 얽힌 큐비트와 메시지 상태를 벨 측정합니다.
    circuit.append([cirq.CNOT(msg, alice), cirq.H(msg)])
    circuit.append(cirq.measure(msg, alice))

    # 밥이 가진 얽힌 큐비트와 벨 측정으로부터 얻은 2개의 고전 비트들을 통해
    # 원래의 양자 메시지 원본을 복구합니다.
    circuit.append([cirq.CNOT(alice, bob), cirq.CZ(msg, bob)])

    return msg, circuit


def main():
    # 원격이동할 무작위 상태를 부호화합니다.
    ranX = random.random()
    ranY = random.random()
    msg, circuit = make_quantum_teleportation_circuit(ranX, ranY)

    # 회로를 시뮬레이션합니다.
    sim = cirq.Simulator()
    message = sim.simulate(cirq.Circuit(
        [cirq.X(msg)**ranX, cirq.Y(msg)**ranY]))

    # 엘리스의 큐비트를 블로흐 구 위에 출력합니다.
    print("Bloch Sphere of Alice's qubit:")
    b0X, b0Y, b0Z = cirq.bloch_vector_from_state_vector(
        message.final_state, 0)
    print("x: ", round(b0X, 4),
          "y: ", round(b0Y, 4),
          "z: ", round(b0Z, 4))

    # 원격이동 회로를 출력합니다.
    print("\nCircuit:")
    print(circuit)

    # 시뮬레이션의 마지막 상태를 저장합니다.
    final_results = sim.simulate(circuit)

    # 밥의 큐비트를 블로흐 구 위에 출력합니다.
    print("\nBloch Sphere of Bob's qubit:")
    b2X, b2Y, b2Z = cirq.bloch_vector_from_state_vector(
        final_results.final_state, 2)
    print("x: ", round(b2X, 4),
          "y: ", round(b2Y, 4),
          "z: ", round(b2Z, 4))


if __name__ == '__main__':
    main()
