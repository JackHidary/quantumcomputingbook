"""써큐에서 매개변수화된 양자 게이트 다루기."""

# 라이브러리들을 가져옵니다.
# (역자주: matplotlib는 매트랩같은 그래프 도식기능이 탁월한 파이썬 라이브러리이며
#         sympy는 심볼릭 파이썬으로 메이플같은 심볼릭 연산을 수행해주는 라이브러리 입니다.)
import matplotlib.pyplot as plt
import sympy

import cirq

# 양자 회로와 큐비트를 가져옵니다.
qbit = cirq.LineQubit(0)
circ = cirq.Circuit()

# 매개변수 이름 `t`인 심볼을 생성합니다.
symbol = sympy.Symbol("t")

# 매개변수화된 양자 게이트를 추가합니다.
circ.append(cirq.XPowGate(exponent=symbol)(qbit))

# 측정하기.
circ.append(cirq.measure(qbit, key="z"))

# 회로를 화면에 출력합니다.
print("Circuit:")
print(circ)

# 매개변수 값을 훑어보기 위해 범위를 정의합니다.
sweep = cirq.Linspace(key=symbol.name, start=0.0, stop=2.0, length=100)

# 정의된 매개변수 범위에서 훑어보면서 회로를 실행해봅니다.
sim = cirq.Simulator()
res = sim.run_sweep(circ, sweep, repetitions=1000)

# 훑어본 범위에서 각 측정 결과값들을 그래프로 도식합니다.
angles = [x[0][1] for x in sweep.param_tuples()]
zeroes = [res[i].histogram(key="z")[0] / 1000 for i in range(len(res))]
plt.plot(angles, zeroes, "--", linewidth=3)

# 그래프를 꾸며봅니다.
plt.ylabel("Frequency of 0 Measurements")
plt.xlabel("Exponent of X gate")
plt.grid()

plt.savefig("param-sweep-cirq.pdf", format="pdf")
