import tkinter as tk
from menu import Menu

class Program:
    def __init__(self):
        self._state = 0
        self.run()

    def run(self):
        root = tk.Tk()
        root.title("Cache memory access time")
        root.geometry("1000x800")

        self.program_logic(root)

        root.mainloop()

    def program_logic(self, root):
        if self._state == 0:
            Menu(root)
            
