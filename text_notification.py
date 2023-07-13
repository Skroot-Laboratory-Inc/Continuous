import tkinter as tk


def createWidget(frame):
    global widget
    widget = tk.Label(frame, text="")


def packWidget():
    widget.pack(fill='x')


def setText(text, font=('Courier', 9, 'bold'), backgroundColor='RoyalBlue4', foregroundColor='white'):
    widget.configure(text=text, font=font, background=backgroundColor, foreground=foregroundColor)
