"""파이퀼에서 간단한 예제 프로그램."""

# 파이퀼 라이브러리를 가져옵니다.
import pyquil

# 양자 프로그램을 생성합니다.
prog = pyquil.Program()

# 고전 레지스터를 정의합니다.
creg = prog.declare("ro", memory_type="BIT", memory_size=1)

# ANOT연산과 0번째 큐비트에 추가하고 그 측정결과를 고전 레지스터에 0번째에 저장합니다.
prog += [
    pyquil.gates.X(0),
    pyquil.gates.MEASURE(0, creg[0])
    ]

# 프로그램을 출력합니다.
print("Program:")
print(prog)

# 회로를 실행할 양자 컴퓨터를 가져옵니다.
computer = pyquil.get_qc("1q-qvm")

# 프로그램을 여러번 실행하도록 설정합니다.
prog.wrap_in_numshots_loop(10)

# 프로그램을 양자 컴퓨터 위에서 실행합니다.
result = computer.run(prog)

# 결과를 출력합니다.
print("Result:")
print(result)
