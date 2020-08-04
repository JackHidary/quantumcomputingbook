"""써큐에서 비트 난수 발생하기."""

# 가져오기
import cirq

# 출력을 위한 보조함수.
def bitstring(bits):
    return ''.join('1' if e else '0' for e in bits)

# 큐비트와 양자회로 얻기
qbit = cirq.LineQubit(0)
circ = cirq.Circuit()

# 아다마르 연산자와 출력 연산을 회로에 추가하기
circ.append([cirq.H(qbit), cirq.measure(qbit, key="z")])

# 회로 시뮬레이션하기
sim = cirq.Simulator()
res = sim.run(circ, repetitions=10)

# 결과 출력하기
print("Bitstring =", bitstring(res.measurements["z"]))
