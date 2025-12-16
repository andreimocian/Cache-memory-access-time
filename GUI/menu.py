import tkinter as tk

class Menu:
    def __init__(self, root):
        self.root = root
        self.render_buttons()

    def render_buttons(self):
        sidebar = tk.Frame(self.root, bg="#1f1f1f", padx=12, pady=12)
        sidebar.pack(side="left", fill="y")

        title = tk.Label(
            sidebar,
            text="Benchmarks",
            bg="#1f1f1f",
            fg="white",
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor="w", pady=(0, 12))

        btn_style = dict(
            width=26,
            anchor="w",
            padx=10,
            pady=10,
            bd=0,
            relief="flat",
            bg="#2b2b2b",
            fg="white",
            activebackground="#3a3a3a",
            activeforeground="white",
            font=("Segoe UI", 11),
            cursor="hand2",
        )

        btn1 = tk.Button(sidebar, text="Linked list test", **btn_style)
        btn1.pack(fill="x", pady=6)

        btn2 = tk.Button(sidebar, text="Matrix multiplication test", **btn_style)
        btn2.pack(fill="x", pady=6)

        btn3 = tk.Button(sidebar, text="Force miss multiplication test", **btn_style)
        btn3.pack(fill="x", pady=6)