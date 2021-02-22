#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Felix D'
__title__ = 'online chess game 1v1 over sockets'
__copyright__ = 'Copyright 2021 by ME'
__license__ = "GPL"
__version__ = '1.0.0'
__date__ = '05.02.2021'
__maintainer__ = "Felix D"
__email__ = "XD@email.de"
__status__ = "Production"

"""
create a gui to which the user can input his target host and port and finally ply chess
"""

import tkinter as tk
from tkinter import messagebox, Entry, Label
from helper import inputs_from_gui

HEIGHT = 250
WIDTH = 400


def process_button_press(host: str, port: str, is_host: str) -> None:
    try:
        print(f"is_host lowwer {is_host, is_host.lower()}")
        if not host or not port or not is_host or is_host.lower() not in 'hc':
            raise Exception('Please fill in all necessary fields')

        is_host_b = True if is_host.lower() == 'h' else False

        inputs_from_gui(host, int(port), is_host_b)

    except Exception as err:
        # Error Pop-Up
        messagebox.showinfo('Chess Error', 'Please fill in all necessary fields.')
        print(f'Error: {err}')


def main() -> None:
    root = tk.Tk()
    root.title('Chess - by Felix D. - v1.0.0')
    root.configure(bg='black')

    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg="black")
    canvas.pack()

    frame = tk.Frame(root, bg='black')
    frame.place(relx=0.05, rely=0.05, relheight=0.9, relwidth=0.9)

    elements = ['Host', 'Port', 'Host_or_Client_[H/C]']
    label_name = entry_name = []
    for e in elements:
        label_name.append('label_' + e)
        entry_name.append('entry_' + e)

    rel_y = 0.1
    for i in range(len(elements)):
        # label
        print(elements[i])
        label_name[i]: Label = tk.Label(frame, text=f'{elements[i]}: ', bg='gray')
        label_name[i].place(relx=0.1, rely=rel_y, relheight=0.1, relwidth=0.4)
        # entry
        entry_name[i]: Entry = tk.Entry(frame, bg="gray")
        entry_name[i].place(relx=0.55, rely=rel_y, relheight=0.1, relwidth=0.4)
        rel_y += 0.15

    # def open_dictionary_attack(url, dictionary_path, email)
    submit_button = tk.Button(frame, text='Connect', bg="gray",
                              command=lambda: process_button_press(
                                  entry_name[0].get(),
                                  entry_name[1].get(),
                                  entry_name[2].get()
                              ))
    submit_button.place(relx=0.1, rely=0.6, relheight=0.1, relwidth=0.3)

    root.mainloop()


if __name__ == '__main__':
    main()
