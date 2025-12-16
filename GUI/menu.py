import tkinter as tk

class Menu:
    def __init__(self, root, on_select):
        self.root = root
        self.on_select = on_select
        self.render_buttons()

    def render_buttons(self):
        sidebar = tk.Frame(self.root, bg="#1f1f1f", padx=12, pady=12)
        sidebar.pack(side="left", fill="y")

        btn_style = dict(
            width=26, anchor="w", padx=10, pady=10, bd=0, relief="flat",
            bg="#2b2b2b", fg="white",
            activebackground="#3a3a3a", activeforeground="white",
            font=("Segoe UI", 11), cursor="hand2",
        )

        tk.Button(
            sidebar,
            text="Linked list test",
            command=lambda: self.on_select(1),
            **btn_style
        ).pack(fill="x", pady=6)

        tk.Button(sidebar, text="Matrix multiplication test",
                  command=lambda: self.on_select(2),
                  **btn_style).pack(fill="x", pady=6)

        tk.Button(sidebar, text="Force miss multiplication test",
                  command=lambda: self.on_select(3),
                  **btn_style).pack(fill="x", pady=6)
