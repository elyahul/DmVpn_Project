import time
import tkinter as tk
from tkinter import ttk

Data_Path = []
__Params__ = ['Jinja Templates Directory', 'Jinja Base Template', 'Jinja Child Template', 'Hub Yaml File',  'Spoke Yaml File']
__Gen__ = (num for num in _Params_[1:])

class MainGUI(ttk.Frame):
    ''' Main GUI window '''
    def __init__(self, master):
        ''' Init main window '''
        ttk.Frame.__init__(self, master=master)
        self.master.title('Main GUI')
        self.style = ttk.Style(master)
        self.style.configure('TFrame', background ='#e1d8a1')
        self.style.configure('TButton', background ='#b1d8b9')
        self.style.configure('TLabel', background ='#e1d8b1', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', background ='#e1d8b9', font=('Arial', 15, 'bold'))
      
        self.frame = ttk.Frame(master, width=400, height=100, relief=tk.SUNKEN)
        self.frame.pack()
        self.sv = tk.StringVar()
        self.logo = tk.PhotoImage(file = '')
        ttk.Label(self.frame, image=self.logo).grid(row=0, column=0, rowspan=2)
        ttk.Label(self.frame, wraplength=100,text='Input Field',
                  font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, sticky = 's')
        self.input_entry = ttk.Entry(self.frame, width=45, textvariable =self.sv)
        self.input_entry.grid(row=2, column=0, padx=5, pady=(2,7))
        self.txtvar = tk.StringVar()
        self.txtvar.set(f'Please input  "{_Params_[1]}" ..')
        self.prevalue = ''
        self.message = tk.Message(self.frame, width=350, bd=10, bg='#e1d8a1',
                                  relief=tk.RIDGE, textvariable=self.txtvar, font=('Arial', 11, 'bold'))
        self.message.grid(row=3, columnspan=2, padx=5, pady=5)
        self.start_button = ttk.Button(self.frame, text='Start', )
        self.start_button.grid(row=5, column=0, padx=5, pady=(12,5), sticky='w')
        self.clear_button = ttk.Button(self.frame, text='Clear', command=self.clear_entry)
        self.clear_button.grid(row=5, column=0, padx=5, pady=(12,5), sticky='e')
        self.submit_button = ttk.Button(self.frame, text='Submit', command=self.submit_ip)
        self.submit_button.grid(row=5, column=0, padx=5, pady=(12,5), sticky='s')
        self.frame.bind_all('<Escape>', func=self.destroy_self)
        self.frame.bind_all("<Return>", func=self.submit_ip)
        self.frame.bind_all("<KP_Enter>", func=self.submit_ip)
        
   
        
    def submit_ip(self, event=None):
        try:
            self.value = self.sv.get()
            print(self.value, self.prevalue)
            if ((self.value != self.prevalue) and (self.value != '')):
                Data_Path.append(self.value)
                self.prevalue = self.value
                self.clear_entry()
                print(Data_Path)
                self.txtvar.set(f'Please input "{next(_Gen_)}" ...')
        except:
                self.txtvar.set(f'Thank you ...')
                self.clear_entry()
                self.destroy_self()
        return Data_Path
  
    def destroy_self(self, event=None):
        self.master.destroy()
        
    def clear_entry(self):
        self.input_entry.delete(0, 'end')

root = tk.Tk()
feedback = MainGUI(root)
root.mainloop()

  


