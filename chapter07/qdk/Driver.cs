using System;

using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;

namespace Quantum.Simple {
    class Driver {
        static void Main(string[] args) {
            // Get a quantum computer simulator
            using (var qsim = new QuantumSimulator()) {
                // Run the operation NotAndMeasure and get the result
                var num_ones = NotAndMeasure.Run(qsim, 10).Result;

                // Print the measurement outcome to the console
                System.Console.WriteLine(
                    $"Number of ones measured: {num_ones, 0}.");
            }
        }
    }
}