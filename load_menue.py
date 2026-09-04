import tkinter as tk
from tkinter import filedialog

from decoder import read_file
from editor import start_editor


def start():
    filename = filedialog.askopenfilename(
        title="Open file",
        filetypes=[
            ("All files", ".untx"),

        ]
    )

    if not filename:
        return

    contents = read_file(filename)
    root.destroy()
    start_editor(contents)

    


if __name__ == "__main__":
    root = tk.Tk()
    root.title("My Editor")

    open_button = tk.Button(
        root,
        text="Open",
        command=start,
        anchor="center",
        padx=10,
        pady=5,
        width=15,
        wraplength=100
    )

    open_button.pack(padx=20, pady=20)

    root.mainloop()
