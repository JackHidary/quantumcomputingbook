"""Simple program in pyQuil."""

# Import the pyQuil library
import pyquil

# Create a quantum program
prog = pyquil.Program()

# Declare a classical register
creg = prog.declare("ro", memory_type="BIT", memory_size=1)

# Add a NOT operation and measurement on a qubit
prog += [
    pyquil.gates.X(0),
    pyquil.gates.MEASURE(0, creg[0])
    ]

# Print the program
print("Program:")
print(prog)

# Get a quantum computer to run on
computer = pyquil.get_qc("1q-qvm")

# Simulate the program many times
prog.wrap_in_numshots_loop(10)

# Execute the program on the computer
result = computer.run(prog)

# Print the results
print("Result:")
print(result)
