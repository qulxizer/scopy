import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FILE = "log.npy"
DOWN_SAMPLE_RATE = 1


# 1. Read Numpy Array
data = np.load(FILE)  # shape (N, 2)
print(type(data))
df = pd.DataFrame(data, columns=["Time", "Voltage"])

# 2. SORT BY TIME
df = df.sort_values("Time").reset_index(drop=True)

# 3. Downsample
df = df.iloc[::DOWN_SAMPLE_RATE]

# 4. Simplify timestamps
df["Time"] = (df["Time"] - df["Time"].iloc[0]).round(3)

# 5. Plot
plt.figure(figsize=(10, 6))
plt.plot(df["Time"], df["Voltage"])
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Voltage vs Time (Sorted)")
plt.grid(True)
plt.show()
