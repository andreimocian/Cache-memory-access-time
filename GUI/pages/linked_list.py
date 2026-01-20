import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import subprocess
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages


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

        self.export_btn = ttk.Button(controls, text="Export to PDF", command=self.export_to_pdf, state="disabled")
        self.export_btn.pack(side="left", padx=5)

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
            sizes, secs, cache_sizes = self._run_exe(mode=mode)
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
        self._plot(series, cache_sizes)

        self.last_data = {
            'mode': label,
            'sizes': sizes,
            'times': secs,
            'cache_sizes': cache_sizes
        }
        self.export_btn.config(state="normal")

        self.last_data = {
            'mode': label,
            'sizes': sizes,
            'times': secs,
            'cache_sizes': cache_sizes
        }
        self.export_btn.config(state="normal")

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
            parts = line.split()
            if len(parts) != 2:
                continue
            sizes.append(int(parts[0]))
            secs.append(float(parts[1]))
        return sizes, secs, cache_sizes

    @staticmethod
    def _ns_per_node(sizes, secs, sizeof_l=32):
        return [(t * 1e9) / (s / sizeof_l) for s, t in zip(sizes, secs)]

    def _plot(self, series, cache_sizes=None):
        self.ax.clear()

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

        for label, sizes, ns in series:
            self.ax.plot(sizes, ns, marker="o", label=label)

        self.ax.set_xscale("log", base=2)
        self.ax.set_title("Linked List")
        self.ax.set_xlabel("Working set size (bytes)")
        self.ax.set_ylabel("ns per node")
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
            initialfile=f"linked_list_{self.last_data['mode'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not filename:
            return

        try:
            with PdfPages(filename) as pdf:
                pdf.savefig(self.fig, bbox_inches='tight')
                
                fig2 = Figure(figsize=(8.5, 11))
                ax2 = fig2.add_subplot(111)
                ax2.axis('off')
                
                title_text = f"Linked List Test Results - {self.last_data['mode']}\n"
                title_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                if self.last_data['cache_sizes']:
                    title_text += "Cache Sizes:\n"
                    for level, size in self.last_data['cache_sizes'].items():
                        title_text += f"  {level}: {size / (1024*1024):.2f} MB ({size:,} bytes)\n"
                    title_text += "\n"
                
                title_text += "Measurement Data:\n"
                title_text += f"{'Size (bytes)':<15} {'Time (s)':<15} {'ns/node':<15}\n"
                title_text += "-" * 45 + "\n"
                
                ns_values = self._ns_per_node(self.last_data['sizes'], self.last_data['times'])
                for size, time, ns in zip(self.last_data['sizes'], self.last_data['times'], ns_values):
                    title_text += f"{size:<15} {time:<15.6f} {ns:<15.2f}\n"
                
                ax2.text(0.1, 0.9, title_text, transform=ax2.transAxes, 
                        fontfamily='monospace', fontsize=10, verticalalignment='top')
                
                pdf.savefig(fig2, bbox_inches='tight')
                
            messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
