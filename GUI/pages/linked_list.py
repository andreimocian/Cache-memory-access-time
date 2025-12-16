import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LinkedListPage:
    def __init__(self, parent):
        self.parent = parent

        self.mode_var = tk.StringVar(value="r")

        self.exe_path = (Path(__file__).resolve().parent.parent / "bin" / "linked-list.exe")

        self._build_ui()

    def _build_ui(self):
        self.frame = tk.Frame(self.parent, bg="#f0f0f0", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="Linked List Test",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w")

        controls = tk.Frame(self.frame, bg="#f0f0f0")
        controls.pack(anchor="w", pady=(12, 10), fill="x")

        tk.Label(controls, text="Select tests:", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left")

        tk.Radiobutton(
            controls, text="Sequential",
            variable=self.mode_var, value="s",
            bg="#f0f0f0"
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            controls, text="Random",
            variable=self.mode_var, value="r",
            bg="#f0f0f0"
        ).pack(side="left", padx=10)

        self.run_btn = ttk.Button(controls, text="Run", command=self.run_selected)
        self.run_btn.pack(side="left", padx=14)

        self.status = tk.Label(self.frame, text="Ready.", bg="#f0f0f0", fg="#333")
        self.status.pack(anchor="w", pady=(0, 10))

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Working set size (bytes)")
        self.ax.set_ylabel("ns per node")
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._draw_empty()

    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_title("Run a test to see results")
        self.ax.set_xlabel("Working set size (bytes)")
        self.ax.set_ylabel("ns per node")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    def run_selected(self):
        if not self.exe_path.exists():
            messagebox.showerror("Missing executable", f"Not found:\n{self.exe_path}")
            return

        self.run_btn.config(state="disabled")
        self.status.config(text="Running…")
        self.frame.update_idletasks()
        mode = self.mode_var.get()

        try:
            sizes, secs = self._run_exe(mode=mode)
            if not sizes:
                raise RuntimeError("No data parsed from program output.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Cannot run:\n{self.exe_path}")
            self.status.config(text="Failed.")
            self.run_btn.config(state="normal")
            return
        except subprocess.CalledProcessError as e:
            msg = (e.stderr or e.stdout or str(e)).strip()
            messagebox.showerror("Benchmark failed", msg[:2000])
            self.status.config(text="Failed.")
            self.run_btn.config(state="normal")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Error.")
            self.run_btn.config(state="normal")
            return
        label = "Sequential" if mode == "s" else "Random"
        series = [(label, sizes, self._ns_per_node(sizes, secs))]
        self._plot(series)

        self.status.config(text="Done.")
        self.run_btn.config(state="normal")


    def _run_exe(self, mode: str):
        res = subprocess.run(
            [str(self.exe_path), mode],
            capture_output=True,
            text=True,
            check=True
        )
        return self._parse_stdout(res.stdout)

    @staticmethod
    def _parse_stdout(text: str):
        sizes, secs = [], []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            sizes.append(int(parts[0]))
            secs.append(float(parts[1]))
        return sizes, secs

    @staticmethod
    def _ns_per_node(sizes, secs, sizeof_l=32):
        return [(t * 1e9) / (s / sizeof_l) for s, t in zip(sizes, secs)]

    def _plot(self, series):
        self.ax.clear()

        self.ax.axvline(2**20, color='gray', linestyle='--', label='~L1 = 2^20 B')
        self.ax.axvline(2**23.5, color='orange', linestyle='--', label='~L2 ≈ 2^23.5 B')
        self.ax.axvline(2**24.5, color='red', linestyle='--', label='~L3 ≈ 2^24.5 B')

        for label, sizes, ns in series:
            self.ax.plot(sizes, ns, marker="o", label=label)

        self.ax.set_xscale("log", base=2)
        self.ax.set_title("Linked List")
        self.ax.set_xlabel("Working set size (bytes)")
        self.ax.set_ylabel("ns per node")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()

        self.canvas.draw()
