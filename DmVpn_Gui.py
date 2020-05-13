import tkinter as tk
import sys
from tkinter import ttk


class MainFrame():
    def __init__(self, master):

        self.frame_header = ttk.Frame(master)
        self.frame_header.pack()
        
        self.logo = tk.PhotoImage(file = '')
        ttk.Label(self.frame_header, image=self.logo).grid(row=0, column=0, rowspan=2)
        ttk.Label(self.frame_header, wraplength=1000,
                  text='DmVpn Constructor Application').grid(row=0, column=1)
        self.frame_body = ttk.Frame(master)
        self.frame_body.pack()
        
        ttk.Label(self.frame_header, text='Hub Ip Address').grid(row=1, column=0, sticky ='sw', padx=5)
        ttk.Label(self.frame_header, text='Spoke Ip Address').grid(row=1, column=1)
        ttk.Label(self.frame_header, text='Instructions').grid(row=4, column=0, sticky ='w')
        self.hub_entry = ttk.Entry(self.frame_header, width=15)
        self.spoke_entry = ttk.Entry(self.frame_header, width=15)

        self.hub_entry.grid(row=2, column=0, padx=5)
        self.spoke_entry.grid(row=2, column=1)

       
        self.text_comments = tk.Text(self.frame_body, width=47, height=10)
        self.text_comments.grid(row=4, column=0, columnspan=2, padx=10, pady=3)
        
        ttk.Button(self.frame_body, text='Submit').grid(row=5, column=0, padx=5, sticky = 'e')
        ttk.Button(self.frame_body, text='Clear').grid(row=5, column=1, padx=3, sticky = 'w')
        
        
    
class Input_Canvas(MainFrame):
    pass
class Error_Canvas(MainFrame):
    pass
class Info_Canvas(MainFrame):
    pass

def main():
    root = tk.Tk()
    mainfraim = MainFrame(root)
    root.mainloop()

if __name__=='__main__': main()
