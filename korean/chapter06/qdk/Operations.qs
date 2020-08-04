namespace Quantum.Simple
{
    // 라이브러리들을 가져옵니다.
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    // 큐비트 하나를 원하는 상태(desired_state)에 있도록 설정합니다.
    operation Set(desired_state: Result, qubit: Qubit) : Unit {
        let current = M(qubit);
        if (current != desired_state) {
            X(qubit);
        }
    }

    // 입력받은 숫자만큼 반복하며 "not and measure" 회로를 실행합니다.
    // 그리고 측정된 1의 개수를 반환합니다.
    operation NotAndMeasure(repetitions: Int) : Int {
        // 측정된 1의 개수를 저장할 변수.
        mutable num_ones = 0;

        // 사용할 큐비트 하나를 가져옵니다.
        using (qubit = Qubit()) {
            // 입력받은 수 repetitions 만큼 반복문을 수행합니다.
            for (test in 1..repetitions) {
                // 큐비트 하나를 |0> 상태로 설정한 후 가져옵니다.
                Set(Zero, qubit);

                // NOT 연산을 수행합니다.
                X(qubit);

                // 큐비트를 측정합니다.
                let res = M (qubit);

                // 우리가 측정한 1의 개수를 세어봅니다.
                if (res == One) {
                    set num_ones = num_ones + 1;
                }
            }
            // System.AggregateException 예외를 피하기 위해 큐비트는 항상 할당 해제할 때
            // |0> 큐비트에 둡니다.
            Set(Zero, qubit);
        }
        // 측정된 1의 개수를 출력합니다.
        return num_ones;
    }
}
