"""Working with parameterized gates in Cirq."""

# Imports
import matplotlib.pyplot as plt

import cirq

# Get a qubit and a circuit
qbit = cirq.LineQubit(0)
circ = cirq.Circuit()

# Get a symbol
symbol = cirq.Symbol("t")

# Add a parameterized gate
circ.append(cirq.XPowGate(exponent=symbol)(qbit))

# Measure
circ.append(cirq.measure(qbit, key="z"))

# Display the circuit
print("Circuit:")
print(circ)

# Get a sweep over parameter values
sweep = cirq.Linspace(key=symbol.name, start=0.0, stop=2.0, length=100)

# Execute the circuit for all values in the sweep
sim = cirq.Simulator()
res = sim.run_sweep(circ, sweep, repetitions=1000)

# Plot the measurement outcomes at each value in the sweep
angles = [x[0][1] for x in sweep.param_tuples()]
zeroes = [res[i].histogram(key="z")[0] / 1000 for i in range(len(res))]
plt.plot(angles, zeroes, "--", linewidth=3)

# Plot options and formatting
plt.ylabel("Frequency of 0 Measurements")
plt.xlabel("Exponent of X gate")
plt.grid()

plt.savefig("param-sweep-cirq.pdf", format="pdf")
