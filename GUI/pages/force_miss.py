import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MatrixMulForceMissPage:
    def __init__(self, parent):
        self.parent = parent

        self.exe_path = (Path(__file__).resolve().parent.parent / "bin" / "force-miss-mul.exe")

        self._build_ui()

    def _build_ui(self):
        self.frame = tk.Frame(self.parent, bg="#f0f0f0", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="Matrix Mul: ikj vs ikj (force miss)",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f0f0",
        ).pack(anchor="w")

        controls = tk.Frame(self.frame, bg="#f0f0f0")
        controls.pack(anchor="w", pady=(12, 10), fill="x")

        self.run_btn = ttk.Button(controls, text="Run", command=self.run_both)
        self.run_btn.pack(side="left")

        self.status = tk.Label(self.frame, text="Ready.", bg="#f0f0f0", fg="#333")
        self.status.pack(anchor="w", pady=(8, 10))

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._draw_empty()

    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_title("Run to see results")
        self.ax.set_xlabel("Size of matrices (bytes)")
        self.ax.set_ylabel("Time (seconds)")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    def run_both(self):
        if not self.exe_path.exists():
            messagebox.showerror("Missing executable", f"Not found:\n{self.exe_path}")
            return

        self.run_btn.config(state="disabled")
        try:
            self.status.config(text="Running ikj…")
            self.frame.update_idletasks()
            sizes_ikj, times_ikj = self._run_mode("m")

            self.status.config(text="Running force miss…")
            self.frame.update_idletasks()
            sizes_fm, times_fm = self._run_mode("f")

            if not sizes_ikj or not sizes_fm:
                raise RuntimeError("No data parsed from benchmark output.")

            self._plot(sizes_ikj, times_ikj, sizes_fm, times_fm)
            self.status.config(text="Done.")

        except subprocess.CalledProcessError as e:
            msg = (e.stderr or e.stdout or str(e)).strip()
            messagebox.showerror("Benchmark failed", msg[:2000])
            self.status.config(text="Failed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Error.")
        finally:
            self.run_btn.config(state="normal")

    def _run_mode(self, mode: str):
        res = subprocess.run(
            [str(self.exe_path), mode],
            cwd=str(self.exe_path.parent),
            capture_output=True,
            text=True,
            check=True,
        )
        return self._parse_stdout(res.stdout)

    @staticmethod
    def _parse_stdout(text: str):
        """
        Parses lines like:
          size 6144, 0.000010 seconds
        """
        sizes, times = [], []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("size "):
                continue

            rest = line[5:]
            if "," not in rest:
                continue
            size_part, time_part = rest.split(",", 1)

            try:
                size_bytes = int(size_part.strip())
            except ValueError:
                continue

            time_part = time_part.strip()
            time_str = time_part.split()[0]
            try:
                sec = float(time_str)
            except ValueError:
                continue

            sizes.append(size_bytes)
            times.append(sec)

        return sizes, times

    def _plot(self, sizes_ikj, times_ikj, sizes_fm, times_fm):
        self.ax.clear()

        self.ax.axvline(2**20, color='gray', linestyle='--', label='~L1 = 2^20 B')
        self.ax.axvline(2**23.5, color='orange', linestyle='--', label='~L2 ≈ 2^23.5 B')
        self.ax.axvline(2**24.5, color='red', linestyle='--', label='~L3 ≈ 2^24.5 B')

        self.ax.plot(sizes_fm, times_fm, marker='o', label='ikj force miss')
        self.ax.plot(sizes_ikj, times_ikj, marker='x', label='ikj')

        self.ax.set_xscale('log', base=2)
        self.ax.set_xlabel('Size of matrices (bytes)')
        self.ax.set_ylabel('Time (seconds)')
        self.ax.set_title("Forcing Misses Time")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()

        self.canvas.draw()
