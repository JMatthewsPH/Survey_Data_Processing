import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/output/daily_fish_results_Andulay MPA.csv")

# Ensure the necessary columns exist
if "Date" not in df.columns or "Total Biomass" not in df.columns:
    raise ValueError("The file must contain 'Date' and 'Total Biomass' columns.")

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(df["Date"], df["Total Biomass"], marker="o", label="Total Biomass")
plt.title("Daily Fish Results")
plt.xlabel("Date")
plt.ylabel("Total Biomass")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
