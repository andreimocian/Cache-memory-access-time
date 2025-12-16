import tkinter as tk
from menu import Menu

from pages.linked_list import LinkedListPage
from pages.matrix_mul import MatrixMulPage
from pages.force_miss import MatrixMulForceMissPage

class Program:
    def __init__(self):
        self._state = 0
        self.run()

    def run(self):
        self.root = tk.Tk()
        self.root.title("Cache memory access time")
        self.root.geometry("1000x800")

        Menu(self.root, self.set_state)

        self.content = tk.Frame(self.root, bg="#f0f0f0")
        self.content.pack(side="left", fill="both", expand=True)

        self.root.mainloop()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def set_state(self, new_state: int):
        self._state = new_state
        print("state =", self._state)

        self.clear_content()

        if self._state == 1:
            LinkedListPage(self.content)
        elif self._state == 2:
            MatrixMulPage(self.content)
        elif self._state == 3:
            MatrixMulForceMissPage(self.content)