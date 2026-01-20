import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import subprocess
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages


class MatrixMulPage:
    def __init__(self, parent):
        self.parent = parent

        self.exe_path = (Path(__file__).resolve().parent.parent / "bin" / "matrix-mul.exe")

        self._build_ui()

    def _build_ui(self):
        self.frame = tk.Frame(self.parent, bg="#f0f0f0", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="Matrix Multiplication Test",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w")

        controls = tk.Frame(self.frame, bg="#f0f0f0")
        controls.pack(anchor="w", pady=(12, 10), fill="x")

        self.run_btn = ttk.Button(controls, text="Run (ijk / ikj / jki)", command=self.run_all)
        self.run_btn.pack(side="left")

        self.export_btn = ttk.Button(controls, text="Export to PDF", command=self.export_to_pdf, state="disabled")
        self.export_btn.pack(side="left", padx=5)

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

    def run_all(self):
        if not self.exe_path.exists():
            messagebox.showerror("Missing executable", f"Not found:\n{self.exe_path}")
            return

        self.run_btn.config(state="disabled")
        self.status.config(text="Running ijk…")
        self.frame.update_idletasks()

        try:
            sizes_i, times_i, cache_sizes = self._run_exe("i")
            self.status.config(text="Running ikj…")
            self.frame.update_idletasks()

            sizes_k, times_k, _ = self._run_exe("k")
            self.status.config(text="Running jki…")
            self.frame.update_idletasks()

            sizes_j, times_j, _ = self._run_exe("j")

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

        self._plot(
            sizes_i, times_i,
            sizes_k, times_k,
            sizes_j, times_j,
            cache_sizes
        )

        self.last_data = {
            'sizes_i': sizes_i, 'times_i': times_i,
            'sizes_k': sizes_k, 'times_k': times_k,
            'sizes_j': sizes_j, 'times_j': times_j,
            'cache_sizes': cache_sizes
        }
        self.export_btn.config(state="normal")

        self.status.config(text="Done.")
        self.run_btn.config(state="normal")

    def _run_exe(self, mode: str):
        res = subprocess.run(
            [str(self.exe_path), mode],
            cwd=str(self.exe_path.parent),
            capture_output=True,
            text=True,
            check=True
        )
        return self._parse_stdout(res.stdout)

    @staticmethod
    def _parse_stdout(text: str):
        sizes, times = [], []
        cache_sizes = {}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if 'L1 size:' in line:
                cache_sizes['L1'] = int(line.split(':')[1].split()[0])
                continue
            elif 'L2 size:' in line:
                cache_sizes['L2'] = int(line.split(':')[1].split()[0])
                continue
            elif 'L3 size:' in line:
                cache_sizes['L3'] = int(line.split(':')[1].split()[0])
                continue
            
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

        return sizes, times, cache_sizes

    def _plot(self, sizes_i, times_i, sizes_k, times_k, sizes_j, times_j, cache_sizes=None):
        self.ax.clear()

        if cache_sizes:
            if 'L1' in cache_sizes:
                self.ax.axvline(cache_sizes['L1'], color='gray', linestyle='--', 
                               label=f"L1 = {cache_sizes['L1'] // (1024*1024)} MB")
            if 'L2' in cache_sizes:
                self.ax.axvline(cache_sizes['L2'], color='orange', linestyle='--', 
                               label=f"L2 = {cache_sizes['L2'] // (1024*1024)} MB")
            if 'L3' in cache_sizes:
                self.ax.axvline(cache_sizes['L3'], color='red', linestyle='--', 
                               label=f"L3 = {cache_sizes['L3'] // (1024*1024)} MB")
        else:
            self.ax.axvline(2**20, color='gray', linestyle='--', label='~L1 = 2^1 B')
            self.ax.axvline(2**23.5, color='orange', linestyle='--', label='~L2 ≈ 2^2 B')
            self.ax.axvline(2**24.5, color='red', linestyle='--', label='~L3 ≈ 2^3 B')

        self.ax.plot(sizes_i, times_i, marker='o', label='ijk')
        self.ax.plot(sizes_k, times_k, marker='x', label='ikj')
        self.ax.plot(sizes_j, times_j, marker='^', label='jki')

        self.ax.set_xscale('log', base=2)
        self.ax.set_xlabel('Size of matrices (bytes)')
        self.ax.set_ylabel('Time (seconds)')
        self.ax.set_title(" Matrix Multiplication Time")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()

        self.canvas.draw()

    def export_to_pdf(self):
        if not hasattr(self, 'last_data'):
            messagebox.showwarning("No Data", "Please run a test first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"matrix_mul_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not filename:
            return

        try:
            with PdfPages(filename) as pdf:
                pdf.savefig(self.fig, bbox_inches='tight')
                
                fig2 = Figure(figsize=(8.5, 11))
                ax2 = fig2.add_subplot(111)
                ax2.axis('off')
                
                title_text = f"Matrix Multiplication Test Results\n"
                title_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                if self.last_data['cache_sizes']:
                    title_text += "Cache Sizes:\n"
                    for level, size in self.last_data['cache_sizes'].items():
                        title_text += f"  {level}: {size / (1024*1024):.2f} MB ({size:,} bytes)\n"
                    title_text += "\n"
                
                for algo, label in [('i', 'ijk'), ('k', 'ikj'), ('j', 'jki')]:
                    sizes = self.last_data[f'sizes_{algo}']
                    times = self.last_data[f'times_{algo}']
                    
                    title_text += f"{label} Algorithm:\n"
                    title_text += f"{'Size (bytes)':>20} {'Time (s)':>15}\n"
                    title_text += "-" * 37 + "\n"
                    
                    for size, time in zip(sizes, times):
                        title_text += f"{size:>20,} {time:>15.6f}\n"
                    title_text += "\n"
                
                ax2.text(0.1, 0.9, title_text, transform=ax2.transAxes, 
                        fontfamily='monospace', fontsize=9, verticalalignment='top')
                
                pdf.savefig(fig2, bbox_inches='tight')
                
            messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
