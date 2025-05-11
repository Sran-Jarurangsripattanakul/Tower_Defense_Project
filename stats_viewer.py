import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def main():
    # Load CSV data
    df = pd.read_csv("game_stats.csv")

    # Create main window
    root = tk.Tk()
    root.title("Game Statistics Dashboard")
    root.geometry("800x600")

    # Create Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # --- Tab 1: Data Table ---
    table_frame = ttk.Frame(notebook)
    notebook.add(table_frame, text="Data Table")

    tree = ttk.Treeview(table_frame, columns=list(df.columns), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for _, row in df.iterrows():
        tree.insert('', 'end', values=list(row))

    # Helper to create chart tabs
    def add_chart_tab(title, plot_func):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        plot_func(ax)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    # --- Plot functions ---
    def plot_enemies(ax):
        ax.plot(df["Wave"], df["Enemies Defeated"], marker='o')
        ax.set_title("Enemies Defeated per Wave")
        ax.set_xlabel("Wave")
        ax.set_ylabel("Enemies Defeated")

    def plot_efficiency(ax):
        ax.scatter(df["Towers Placed"], df["Placement Effectiveness"])
        ax.set_title("Placement Efficiency")
        ax.set_xlabel("Towers Placed")
        ax.set_ylabel("Effectiveness")

    def plot_damage(ax):
        ax.bar(df["Wave"], df["Damage Dealt"])
        ax.set_title("Damage Dealt per Wave")
        ax.set_xlabel("Wave")
        ax.set_ylabel("Damage Dealt")

    def plot_wave_time(ax):
        ax.hist(df["Wave Time (ms)"], bins=10)
        ax.set_title("Wave Completion Time Distribution")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Frequency")

    def plot_spending(ax):
        waves  = df["Wave"].astype(str).tolist()
        spends = df["Currency Spent"].tolist()

        # # Option A: Bar chart of spending per wave
        # ax.bar(waves, spends)
        # ax.set_title("Currency Spent per Wave")
        # ax.set_xlabel("Wave")
        # ax.set_ylabel("Currency Spent")

        # Option B: Pie chart of spend distribution
        # Uncomment below to use pie instead
        ax.clear()
        ax.pie(spends, labels=waves, autopct='%1.1f%%')
        ax.set_title("Spend Distribution Across Waves")

    # Add the chart tabs
    add_chart_tab("Enemies Defeated", plot_enemies)
    add_chart_tab("Efficiency", plot_efficiency)
    add_chart_tab("Damage Dealt", plot_damage)
    add_chart_tab("Wave Time", plot_wave_time)
    add_chart_tab("Resource Utilization", plot_spending)

    root.mainloop()

if __name__ == "__main__":
    main()
