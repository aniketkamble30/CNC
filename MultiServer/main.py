# import tkinter as tk
# from tkterminal import Terminal

# root = tk.Tk()
# terminal = Terminal(pady=5, padx=5)
# terminal.shell = True
# terminal.linebar = True
# terminal.pack(expand=True, fill='both')
# b1 = tk.Button(
#     root, text="Start Server", fg="Black",
#     command=lambda: terminal.run_command('python server.py', 'y'))
# b1.pack()

# b2 = tk.Button(
#     root, text="LIST", fg="Black",
#     command=lambda: terminal.run_command('list', 'y'))
# b2.pack()
# root.mainloop()

from tkinter import *
import os

root = Tk()
termf = Frame(root, height=800, width=800)

termf.pack(expand=YES)
wid = termf.winfo_id()
os.system('xterm -into %d -geometry 100x100 -sb &' % wid)
b1 = tk.Button(
    root, text="Start Server", fg="white",
    command=lambda: terminal.run_command('python server.py', 'y'))
b1.pack(padx=10)
root.mainloop()