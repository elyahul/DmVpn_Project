import tkinter as tk
import sys
from tkinter import ttk
import ipaddress


class MainFrame():
    def __init__(self, master):
        master.title('DmVpn Constructor Application')
    
        self.style = ttk.Style()
        self.style.configure('TFrame', background ='#e1d8a1')
        self.style.configure('TButton', background ='#b1d8b9')
        self.style.configure('TLabel', background ='#e1d8b9', font=('Arial', 11, 'bold'))
        self.style.configure('Header.TLabel', background ='#e1d8b9')
        
        self.panedwindow = ttk.PanedWindow(master, orient=tk.VERTICAL)
        self.panedwindow.pack()
        self.frame_header = ttk.Frame(self.panedwindow, width=350, height=100, relief=tk.SUNKEN)
        self.frame_body = ttk.Frame(self.panedwindow, width=350, height=300)
        self.panedwindow.add(self.frame_header, weight=1)
        self.panedwindow.add(self.frame_body, weight=4)
        
        self.logo = tk.PhotoImage(file = '')
        ttk.Label(self.frame_header, image=self.logo).grid(row=0, column=0, rowspan=2)
        ttk.Label(self.frame_header, wraplength=500,
                  text='Input Fields').grid(row=0, column=0, columnspan=2, sticky = 's')
        
        
        ttk.Label(self.frame_header, text='Hub Ip Address').grid(row=1, column=0, sticky ='s')
        ttk.Label(self.frame_header, text='Spoke Ip Address').grid(row=1, column=1, sticky = 'se', padx=15 )
        ttk.Label(self.frame_body, text='Program Execution  Stages', font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, padx=25, sticky='s')
        self.hub_entry = ttk.Entry(self.frame_header, width=15)
        self.spoke_entry = ttk.Entry(self.frame_header, width=15)

        self.hub_entry.grid(row=2, column=0, padx=15)
        self.spoke_entry.grid(row=2, column=1, sticky= 'e', padx = 15)

##        self.progressbar = tk.Progressbar(self.frame_header, length= 20)
##        self.progressbar.pack()
##        self.progressbar.grid(row=5, column=0,padx=5,columnspan=2)
        
##        var.set('Please input Hub and Spoke ip addresses...')
        self.message = tk.Message(self.frame_body, width=300, bd=10, 
                                  bg='lightgreen', relief=tk.RIDGE)
        self.message.grid(row=1, columnspan=2, padx=10, pady=3)
        
       
        ttk.Button(self.frame_body, text='Submit', command=self.submit).grid(row=2, column=0, padx=5, sticky = 'e')
        ttk.Button(self.frame_body, text='Clear', command=self.clear).grid(row=2, column=1, padx=3, sticky = 'w')
        

    def clear(self):
        self.hub_entry.delete(0, 'end')
        self.spoke_entry.delete(0, 'end')
        

    def submit(self):
        self.Hub_IP = self.hub_entry.get()
        self.Spoke_IP = self.spoke_entry.get()
        
        return  Hub_IP,Spoke_IP
    
    def check_ip(self,ip):                                           ##Function to chek ip adress sanity
        try:
            ipaddress.ip_address(ip)
        except ValueError as e:
            print('#Wrong Ip Address...',e)
            return False 
        
        
    
class Input_Canvas(MainFrame):
    pass
class Error_Canvas(MainFrame):
   pass
    
class Info_Canvas(MainFrame):
    def messagebox():
        messagebox.showinfo(title = 'Wrong Ip Address...')




def main():
    root = tk.Tk()
    mainframe = MainFrame(root)
    for ip in DEVICES_IP_LIST:
        mainframe.check_ip(ip)
    root.mainloop()
    

if __name__=='__main__':
    
    Hub_IP  = ""
    Spoke_IP = ""
    DEVICES_IP_LIST = [Hub_IP,Spoke_IP]
    main()
