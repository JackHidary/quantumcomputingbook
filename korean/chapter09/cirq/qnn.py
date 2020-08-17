"""양자 신경 회로망 써큐 예제."""

# 가져오기
import cirq
import matplotlib.pyplot as plt
import numpy as np
import sympy

# ZX 게이트를 써큐에서 구현하기 위한 클래스
class ZXGate(cirq.ops.eigen_gate.EigenGate,
             cirq.ops.gate_features.TwoQubitGate):
  """weight를 변수로 갖는 ZXGate."""

  def __init__(self, weight=1):
    """ZX 게이트를 초기화하기.

     Args:
         weight: 주기가 2인 회전각.
    """
    self.weight = weight
    super().__init__(exponent=weight) # 1이 아닌 weight를 자동으로 처리.

  def _eigen_components(self):
    return [
        (1, np.array([[0.5, 0.5, 0, 0],
                      [ 0.5, 0.5, 0, 0],
                      [0, 0, 0.5, -0.5],
                      [0, 0, -0.5, 0.5]])),
        (-1, np.array([[0.5, -0.5, 0, 0],
                      [ -0.5, 0.5, 0, 0],
                      [0, 0, 0.5, 0.5],
                      [0, 0, 0.5, 0.5]]))
    ]

  # 이 함수는 weight가 Symbol이 될 수 있게 합니다. 매개변수화 할때 유용한 함수입니다.
  def _resolve_parameters_(self, param_resolver):
    return ZXGate(weight=param_resolver.value_of(self.weight))

  # 게이트가 ASCII 회로도에서 어떻게 보여야 할까요?
  def _circuit_diagram_info_(self, args):
    return cirq.protocols.CircuitDiagramInfo(
           wire_symbols=('Z', 'X'),
           exponent=self.weight)

# 데이터 큐비트의 총 개수
INPUT_SIZE = 9

data_qubits = cirq.LineQubit.range(INPUT_SIZE)
readout = cirq.NamedQubit('r')

# 회로의 매개변수를 초기화합니다.
params = {'w': 0}

def ZX_layer():
  """각각의 데이터 큐비트와 출력(readout) 큐비트 사이에 ZX게이트를 추가합니다.
  모든 게이트가 한 개의 weight에 대한 동일한 sympy.Symbol객체를 받습니다."""
  for qubit in data_qubits:
    yield ZXGate(sympy.Symbol('w')).on(qubit, readout)


qnn = cirq.Circuit()
qnn.append(ZX_layer())
qnn.append([cirq.S(readout)**-1, cirq.H(readout)]) # Basis transformation

def readout_expectation(state):
  """양자 상태를 의미하는 0과 1으로 이루어진 배열을 입력받고 출력 큐비트에서 측정한 Z의 기대값을
  반환합니다. 써큐의 Simulator를 사용하여 파동함수(wavefunction)를 정확하게 계산합니다."""

  # 상태를 표현하는 편리한 방법은 정수로 나타내는 것입니다.
  state_num = int(np.sum(state*2**np.arange(len(state))))

  resolver = cirq.ParamResolver(params)
  simulator = cirq.Simulator()

  # 큐비트 순서를 명시하여 어떠한 큐비트가 출력 큐비트 readout인지 알 수 있습니다.
  result = simulator.simulate(qnn, resolver, qubit_order=[readout]+data_qubits,
                              initial_state=state_num)
  wf = result.final_state

  # 큐비트의 순서를 정했기 때문에 readout 큐비트의 Z 값은 최상위비트입니다.
  Z_readout = np.append(np.ones(2**INPUT_SIZE), -np.ones(2**INPUT_SIZE))

  # np.real함수를 사용해 허수부를 날려줍니다.
  return np.real(np.sum(wf*wf.conjugate()*Z_readout))

def loss(states, labels):
  loss=0
  for state, label in zip(states,labels):
    loss += 1 - label*readout_expectation(state)
  return loss/(2*len(states))

def classification_error(states, labels):
  error=0
  for state,label in zip(states,labels):
    error += 1 - label*np.sign(readout_expectation(state))
  return error/(2*len(states))

def make_batch():
  """레이블의 집합을 생성하고 입력을 생성하는데 이 레이블들을 사용합니다. label = -1은 상태에서
  0의 개수가 더 많다는 것을 의미하고, label = +1은 1의 개수가 더 많다는 것을 의미힙니다.
  """
  np.random.seed(0) # 데모의 일관성을 위해 씨앗값을 상수로 둡니다.
  labels = (-1)**np.random.choice(2, size=100) # 더 작은 크기가 계산을 빠르게합니다.
  states = []
  for label in labels:
    states.append(np.random.choice(2, size=INPUT_SIZE, p=[0.5-label*0.2,0.5+label*0.2]))
  return states, labels

states, labels = make_batch()

linspace = np.linspace(start=-1, stop=1, num=80)
train_losses = []
error_rates = []
for p in linspace:
  params = {'w': p}
  train_losses.append(loss(states, labels))
  error_rates.append(classification_error(states, labels))
plt.plot(linspace, train_losses)
plt.xlabel('Weight')
plt.ylabel('Loss')
plt.title('Loss as a Function of Weight')
plt.show()
