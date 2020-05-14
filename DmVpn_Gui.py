import tkinter as tk
import sys
from tkinter import ttk
import ipaddress
import time


class MainFrame():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('DmVpn Constructor Application')
      
        self.style = ttk.Style()
        self.style.configure('TFrame', background ='#e1d8a1')
        self.style.configure('TButton', background ='#b1d8b9')
        self.style.configure('TLabel', background ='#e1d8b9', font=('Arial', 11, 'bold'))
        self.style.configure('Header.TLabel', background ='#e1d8b9')
        
        self.panedwindow = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
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
        ttk.Label(self.frame_body, text='Program Execution  Stages',
                  font=('Arial', 14, 'bold')).grid(row=0, column=0,
                  columnspan=2, padx=25, sticky='s')
        self.hub_entry = ttk.Entry(self.frame_header, width=15)
        self.hub_entry.grid(row=2, column=0, padx=15)
        self.spoke_entry = ttk.Entry(self.frame_header, width=15)
        self.spoke_entry.grid(row=2, column=1, sticky= 'e', padx = 15)
        
##        self.progressbar = tk.Progressbar(self.frame_header, length= 20)
##        self.progressbar.pack()
##        self.progressbar.grid(row=5, column=0,padx=5,columnspan=2)
##        var.set('Please input Hub and Spoke ip addresses...')
        self.message = tk.Message(self.frame_body, width=300, bd=10, 
                                  bg='lightgreen', relief=tk.RIDGE)
        self.message.grid(row=1, columnspan=2, padx=10, pady=3)
        
        self.clear_button = ttk.Button(self.frame_body, text='Clear', command=self.clear_entry)
        self.clear_button.grid(row=2, column=1, padx=3, sticky = 'w')
        self.submit_button = ttk.Button(self.frame_body, text='Submit', command=self.submit_ip)
        self.submit_button.grid(row=2, column=0, padx=5, sticky = 'e')

        self.root.mainloop()
        
        self.Hub_IP = ''
        self.Spoke_IP = ''
        self.Devices_IP_List = []

    def destroy_self(self):
        self.root.destroy()
        
    def clear_entry(self):
        self.hub_entry.delete(0, 'end')
        self.spoke_entry.delete(0, 'end')
        
    def submit_ip(self):
        flag = True
        self.Hub_IP = self.hub_entry.get()
        if self.check_ip(self.Hub_IP) == False:
            self.clear_entry()
            print("Wrong IP")
            flag = False
        else:
            self.Spoke_IP = self.spoke_entry.get()
            if self.check_ip(self.Spoke_IP) == False:
                self.clear_entry()
                print("Wrong IP")
                flag = False
        if flag == True:
            self.Devices_IP_List = [self.Hub_IP, self.Spoke_IP]
            time.sleep(1.5)
            self.destroy_self()
            print(" Ip Accepted")
        return  self.Devices_IP_List, self.Hub_IP, self.Spoke_IP
    
    @staticmethod
    def check_ip(ip):                   ##Function to chek ip adress sanity
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError as er:  
            print(er)
            return False

##class Worker():
##    def __init__(self):
##        print("Work Started")
##    root.destroy()
    
    
        
def main():
    mainframe = MainFrame()

main()
