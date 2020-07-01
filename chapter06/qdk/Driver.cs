using System;

using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;

namespace Quantum.Simple {
    class Driver {
        static void Main(string[] args) {
            // 양자 컴퓨터 시뮬레이터를 가져옵니다.
            using (var qsim = new QuantumSimulator()) {
                // NotAndMeasure 연산을 수행하고 그 결과를 가져옵니다.
                var num_ones = NotAndMeasure.Run(qsim, 10).Result;

                // 측정 결과를 콘솔에 출력합니다.
                System.Console.WriteLine(
                    $"Number of ones measured: {num_ones, 0}.");
            }
        }
    }
}