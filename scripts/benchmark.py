import numpy as np

# Load the .npy file
data = np.load("log.npy")  # shape (N, 2) -> [time, voltage]

# Extract timestamps
times = data[:, 0]

# Compute metrics
first_time = times[0]
last_time = times[-1]
n_samples = len(times)

interval = last_time - first_time
rate = n_samples / interval

print(f"Samples: {n_samples}")
print(f"Time span: {interval:.8f} s")
print(f"Effective sampling rate: {rate:.2f} Hz")

