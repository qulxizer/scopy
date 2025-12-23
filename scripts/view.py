import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FILE = "log.npy"


# 1. Read Numpy Array
data: np.ndarray = np.load(FILE)  # shape (N, 2)
df = pd.DataFrame(data, columns=["Time", "Voltage"])

# 2. SORT BY TIME
df = df.sort_values("Time").reset_index(drop=True)

# 3. Simplify timestamps
df["Time"] = (df["Time"] - df["Time"].iloc[0]).round(3)

# 4. Plot
plt.figure(figsize=(10, 6))
(line,) = plt.plot(df["Time"], df["Voltage"])
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Voltage vs Time (Sorted)")
plt.grid(True)
ydata = line.get_ydata()
print("graph data")
print(np.max(ydata), np.min(ydata))
print(np.isnan(ydata).any(), np.isinf(ydata).any())
plt.show()
