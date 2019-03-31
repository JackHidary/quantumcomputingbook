"""Variational quantum eigensolver in pyQuil."""

# Imports
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from pyquil.quil import Program
import pyquil.api as api
from pyquil.paulis import sZ
from pyquil.gates import RX

from grove.pyvqe.vqe import VQE

# Get a QVM Connection. NOTE: This requires the qvm to be running
qvm = api.QVMConnection()

# Function to create the ansatz
def small_ansatz(params):
    """Returns an ansatz Program with one parameter."""
    return Program(RX(params[0], 0))

# Show the ansatz with an example value for the parameter
print("Ansatz with example value for parameter:")
print(small_ansatz([1.0]))

# Create a Hamltion H = Z_0
hamiltonian = sZ(0)

# Make an instance of VQE with a Nelder-Mead minimizer
vqe_inst = VQE(minimizer=minimize,
               minimizer_kwargs={'method': 'nelder-mead'})
        
# Check the VQE manually at a particular angle - say 2.0 radians                  
angle = 2.0
print("Expectation of Hamiltionian at angle = {}".format(angle))
print(vqe_inst.expectation(small_ansatz([angle]), hamiltonian, 10000, qvm))           

# Loop over a range of angles and plot expectation without sampling
angle_range = np.linspace(0.0, 2.0 * np.pi, 20)
exact = [vqe_inst.expectation(small_ansatz([angle]), hamiltonian, None, qvm)
         for angle in angle_range]

# Plot the exact expectation
plt.plot(angle_range, exact, linewidth=4)

# Loop over a range of angles and plot expectation with sampling 
sampled = [vqe_inst.expectation(small_ansatz([angle]), hamiltonian, 1000, qvm)
           for angle in angle_range]

# Plot the sampled expectation
plt.plot(angle_range, sampled, "-o")

# Plotting options
plt.xlabel('Angle [radians]')
plt.ylabel('Expectation value')
plt.grid()
plt.show()

# Do the minimization and return the best angle
initial_angle = [0.0]
result = vqe_inst.vqe_run(small_ansatz, hamiltonian, initial_angle, None, qvm=qvm)
print("\nMinimum energy =", round(result["fun"], 4))
print("Best angle =", round(result["x"][0], 4))
