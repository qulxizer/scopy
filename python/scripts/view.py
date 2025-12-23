import pandas as pd
import matplotlib.pyplot as plt

FILE = "log.csv"
DOWN_SAMPLE_RATE = 10

# 1. Read CSV
df = pd.read_csv(FILE)

# 2. SORT BY TIME (The fix)
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
