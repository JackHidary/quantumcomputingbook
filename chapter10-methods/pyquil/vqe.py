"""Variational quantum eigensolver in pyQuil."""

# Imports
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from pyquil.quil import Program
import pyquil.api as api
from pyquil.paulis import sZ
from pyquil.gates import RX, X, MEASURE

from grove.pyvqe.vqe import VQE

# ============================
# VQE on a noiseless simulator
# ============================
print()
print(" VQE on a noiseless simulator ".center(80, "="))
print()

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

# =======================================
# VQE on a noisy simulator: Pauli Channel
# =======================================
print()
print(" VQE on a noisy simulator: Pauli channel ".center(80, "="))
print()

# Create a noise model which has a 10% chance of each gate at each timestep
pauli_channel = [0.1, 0.1, 0.1]
noisy_qvm = api.QVMConnection(gate_noise=pauli_channel)

# Check that the simulator is indeed noisy
p = Program(X(0), MEASURE(0, 0))
res = noisy_qvm.run(p, [0], 10)
print("Outcome of NOT and MEASURE circuit on noisy simulator:")
print(res)

# Update the minimizer in VQE to start with a larger initial simplex
vqe_inst.minimizer_kwargs = {"method": "Nelder-mead", 
                             "options": 
                                 {"initial_simplex": np.array([[0.0], [0.05]]), 
                                  "xatol": 1.0e-2}
                                 }

# Loop over a range of angles and plot expectation with sampling 
sampled = [vqe_inst.expectation(small_ansatz([angle]), hamiltonian, 1000, noisy_qvm)
           for angle in angle_range]

# Plot the sampled expectation
plt.plot(angle_range, sampled, "-o")

# Plotting options
plt.title("VQE on a Noisy Simulator")
plt.xlabel("Angle [radians]")
plt.ylabel("Expectation value")
plt.grid()
plt.show()

# Study the effect of increasing noise in VQE
data = []
noises = np.linspace(0.0, 0.33, 10)
for noise in noises:
    pauli_channel = [noise] * 3
    # We can pass the noise params directly into vqe_run 
    # instead of passing the noisy connection
    result = vqe_inst.vqe_run(small_ansatz, hamiltonian, initial_angle,
                          gate_noise=pauli_channel)
    data.append(result['fun'])

# Plot the ground state energy vs noise level
plt.plot(noises, data)
plt.xlabel('Noise level')
plt.ylabel('Eigenvalue')
plt.show()

# ===========================================
# VQE on a noisy simulator: Measurement error
# ===========================================
print()
print(" VQE on a noisy simulator: Measurement error ".center(80, "="))
print()

# Measurement noise
measure_noise = [0.1, 0.1, 0.1]

# Noisy QVM with the measurement noise
noisy_meas_qvm = api.QVMConnection(measurement_noise=measure_noise)

# Check that the simulator is indeed noisy
p = Program(X(0), MEASURE(0, 0))
res = noisy_qvm.run(p, [0], 10)
print("Outcome of NOT and MEASURE circuit on noisy measurement simulator:")
print(res)

# Study the effect of increasing measurement noise in VQE
data = []
noises = np.linspace(0.0, 0.5, 20)
for noise in noises:
    measure_noise = [noise] * 3
    noisy_qvm = api.QVMConnection(measurement_noise=measure_noise)
    result = vqe_inst.vqe_run(small_ansatz, hamiltonian, initial_angle, samples=10000, qvm=noisy_qvm)
    data.append(result['fun'])

# Plot the ground state energy vs noise level
plt.plot(noises, data)
plt.xlabel('Noise level %')
plt.ylabel('Eigenvalue')
plt.show()
