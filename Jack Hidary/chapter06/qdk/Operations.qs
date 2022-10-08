namespace Quantum.Simple
{
    // Importing the libraries
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    // Sets a qubit in a desired state
    operation Set(desired_state: Result, qubit: Qubit) : Unit {
        let current = M(qubit);
        if (current != desired_state) {
            X(qubit);
        }
    }

    // Executes the "not and measure" circuit for an input number
    // of repetitions and returns the number of ones measured
    operation NotAndMeasure(repetitions: Int) : Int {
        // Variable to store the number of measured ones
        mutable num_ones = 0;

        // Get a qubit to use
        using (qubit = Qubit()) {
            // Loop over the desired number of repetitions
            for (test in 1..repetitions) {
                // Get a qubit in the zero state
                Set(Zero, qubit);

                // Perform a NOT operation
                X(qubit);

                // Measure the qubit
                let res = M (qubit);

                // Keep track of the number of ones we measured
                if (res == One) {
                    set num_ones = num_ones + 1;
                }
            }
            // "Released qubits" must be in the zero state to avoid a System.AggregateException
            Set(Zero, qubit);
        }
        // Return the number of ones measured
        return num_ones;
    }
}
