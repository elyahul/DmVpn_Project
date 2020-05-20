import tkinter as tk
import sys
from tkinter import ttk
import ipaddress
import time
from tkinter import messagebox
from tkinter import simpledialog
import yaml
import netmiko
import threading
from threading import Thread
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
import sys
import ipaddress
from jinja2 import FileSystemLoader,Environment
from queue import Queue
from datetime import datetime
from operator import itemgetter
from threaded_ssh_gui import send_config, threads_conn
import subprocess
from  subprocess import SubprocessError

COMMAND_LIST = [
        ('show run | s bgp'),
        ('show ip route',
         'show ip interface brief',
         'show run | include hostname'),]

class MainFrame():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('DmVpn Constructor Application')
        self.style = ttk.Style()
        self.style.configure('TFrame', background ='#e1d8a1')
        self.style.configure('TButton', background ='#b1d8b9')
        self.style.configure('TLabel', background ='#e1d8b1', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', background ='#e1d8b9', font=('Arial', 15, 'bold'))
        
        self.panedwindow = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.panedwindow.pack()
        
        self.frame_header = ttk.Frame(self.panedwindow, width=500, height=100, relief=tk.SUNKEN)
        self.frame_body = ttk.Frame(self.panedwindow, width=500, height=300)
        self.panedwindow.add(self.frame_header, weight=1)
        self.panedwindow.add(self.frame_body, weight=4)
        
        self.logo = tk.PhotoImage(file = '')
        ttk.Label(self.frame_header, image=self.logo).grid(row=0, column=0, rowspan=2)
        ttk.Label(self.frame_header, wraplength=100,
                  text='Input Fields', font=('Arial', 11, 'bold')).grid(row=0, column=1, columnspan=2, sticky = 's')
        ttk.Label(self.frame_header, text='Hub Ip Address').grid(row=1, column=0, sticky ='s')
        ttk.Label(self.frame_header, text='Spoke Ip Address').grid(row=1, column=3, sticky = 'e', padx=8 )
        self.hub_entry = ttk.Entry(self.frame_header, width=15)
        self.hub_entry.grid(row=2, column=0, padx=15,pady=(2,7))
        self.spoke_entry = ttk.Entry(self.frame_header, width=15)
        self.spoke_entry.grid(row=2, column=3, sticky='e', padx=7,pady=(2,7))
        
        self.txtvar = tk.StringVar()
        self.txtvar.set('Please Input Hub and Spoke Ip Addresses')
        self.message = tk.Message(self.frame_body, width=350, bd=10, bg='#e1d8a1',
                                  relief=tk.RIDGE, textvariable=self.txtvar, font=('Arial', 12, 'bold'))
        self.message.grid(row=1, columnspan=2, padx=10, pady=5)
        
        self.clear_button = ttk.Button(self.frame_body, text='Clear', command=self.clear_entry)
        self.clear_button.grid(row=2, column=1, padx=5, pady=(12,5), sticky='w')
        self.submit_button = ttk.Button(self.frame_body, text='Submit', command=self.submit_ip)
        self.submit_button.grid(row=2, column=0, padx=5, pady=(12,5), sticky='e')
        self.root.bind('<Escape>', func=self.destroy_self)
        self.root.bind("<Return>", func=self.submit_ip)
        self.root.bind("<KP_Enter>", func=self.submit_ip)
        self.root.mainloop()
        
    @staticmethod                       # Function to chek ip adress sanity
    def check_ip(ip):                   
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError as err:  
            tk.messagebox.showerror(title="Input Error", message=err)
            return False
      
                         
    def pingable(self, ip):             # function to check device reachability
        self.retry = None
        try:
            result = subprocess.call(["ping", "-c 1", ip], stdout=subprocess.PIPE)
            if result == 1:
                tk.messagebox.showinfo(message=f"Device {ip} is unreachable !!!")
        except  SubprocessError as err:
            tk.messagebox.showinfo(message=err)
        return result
    
    def destroy_self(self, event=None):
        self.root.destroy()
        
    def clear_entry(self):
        self.hub_entry.delete(0, 'end')
        self.spoke_entry.delete(0, 'end')

    def submit_ip(self, event=None):
        COUNT = 0
        global Hub_Ip, Spoke_Ip
        flag = True
        Hub_Ip = self.hub_entry.get()
        if self.check_ip(Hub_Ip) == False:
            self.clear_entry()
            self.txtvar.set("Please Try Again. Input the correct  Ip's")
            flag = False
        else:
            Spoke_Ip = self.spoke_entry.get()
            if self.check_ip(Spoke_Ip) == False:
                self.clear_entry()
                self.txtvar.set("Please Try Again. Input the correct  Ip's")
                flag = False
        if flag == True:
            key_list=['device_type', 'ip', 'username', 'password']
            listglobal=['cisco_ios', 'elil', 'cisco']
            listglobal.insert(1, Hub_Ip)
            listglobal1=['cisco_ios', 'elil', 'cisco']
            listglobal1.insert(1, Spoke_Ip)
            device1 = dict(zip(key_list,listglobal))    # define dictionary for devices 
            device2 = dict(zip(key_list,listglobal1))
            devices=[device1,device2]                     
            self.txtvar.set("Ip's are accepted. Starting application ...")
            time.sleep(0.5)
            result = tk.messagebox.askyesno(message="Ip's are Accepted\n  Continue?")
            if result == False:        # exit program if "No" button pressed 
                self.message.grid(row=1, columnspan=2, padx=80, pady=5)
                self.txtvar.set(' Exiting  application ..')
                self.root.after(2000, self.root.destroy)
              
        for device in devices:                             # check connectivity to devices
            reachable = self.pingable(device["ip"])
            COUNT += reachable
        if COUNT == 0:                                    
            self.config_collector(devices, COMMAND_LIST)       # collects data from devies
            self.config_parser()                               # parses data
            spoke_jinja_cfg = Files_Constructor(r'/home/elil/Yml/SPOKE_DICT.yml') # Instaniate Class
            hub_jinja_cfg = Files_Constructor(r'/home/elil/Yml/HUB_DICT.yml')     # Instaniate Class
            spoke_jinja_cfg.create_yaml_file(bgp_dict, 'w')    # Configuring YAML file for Spoke
            spoke_jinja_cfg.create_yaml_file(spoke_dict, 'a')  # Configuring YAML file for Spoke
            hub_jinja_cfg.create_yaml_file(hub_dict, 'w')      # Configuring YAML file for Hub
            # Create Spoke configuration template with Jinja2
            self.result1 = spoke_jinja_cfg.constructor(r"/home/elil/Templates/", r'child_spoke_config_j2')
            # Create Hub configuration template with Jinja2
            self.result2 = hub_jinja_cfg.constructor(r"/home/elil/Templates/", r'hub_config_j2')
            self.cfg_compile()                                 # finalizing configuration of devices
            threads_conn(send_config, devices, 2, self.cfg_list)    # send configuration to devices
            proceed = messagebox.askyesno(message='Spoke device is added to DmVpn cloud. Would you like to configure next device ?')
            if proceed == True:
                self.root.lift()                          
                self.root.focus_force()
            else:
                self.root.destroy()
        else:
            self.clear_entry()
            self.retry = tk.messagebox.askretrycancel(message="Retry?  Quit Application?")
            if self.retry == True:
                self.clear_entry()
                self.txtvar.set("Check devices reachability before input")
            else:
                self.root.destroy()
        return Hub_Ip, Spoke_Ip
    
    def netmiko_ssh(self, args):               # main function for ssh connection 
        self.ssh = ConnectHandler(**args)
        def send_show(command):
            return self.ssh.send_command(command)    
        return send_show
        
    def config_collector(self,params,commands): # funtion collets data from devices
        self.root.iconify()
        global mq_dict
        queue = Queue()
        for device,command in zip(params,commands):
            try:
                self.result=tk.messagebox.askokcancel(message=f'Procced with connection to device {device["ip"]} ?')
                if self.result==False:          # exit program if "Cancel" button pressed
                    self.root.destroy()
                Session = self.netmiko_ssh(device)      # connects to device
                if type(command) == str:
                    queue.put(Session(command))         # gets device configuration
                else:
                    for cfg in command:
                        queue.put(Session(cfg))         # add device output to the queue
                        
            except  NetMikoAuthenticationException as err:
                tk.messagebox.showerror(message=err)
            except  NetMikoTimeoutException as err:
                tk.messagebox.showerror(message=err)
                
        value_list = []                                   # define values list
        key_list = ['hub_bgp_list', 'sir_str' , 'sib_str', 'hostname'] # define keys list
        while not queue.empty():
            value_list.append(queue.get(timeout=2))       # get data from the queue

        mq_dict = dict(zip(key_list, value_list))         # define intermediate dict               
        return mq_dict
    
    def config_parser(self):
        global  hub_dict, spoke_dict, bgp_dict  ## define global variables for YAML file 
        bgp_neigbors = []                       ## List of Hub Current BGP Neigbors
        bgp_dict = {'bgp':bgp_neigbors}         ## Bgp Neigbors Dictionary(For Yaml)
        for key,value in mq_dict.items():
            globals().update(mq_dict)
            
        ''' Get Data from Hub Configuration and create Yaml File '''
        ([bgp_neigbors.append(line) for line in hub_bgp_list.splitlines()
          if ('neighbor' and 'remote-as') in line])

        ''' Get Data from Spoke Configuration  and create dictionary for Yaml File '''
        for line in sib_str.splitlines()[2:]:
            iface,ip,*_,status,proto = line.split()
            if (ip != 'unassigned' and  (status and proto == 'up')):
                if not (iface.startswith('L') or iface.startswith('T')):
                    octet2 = int(ip[3:6])+100
                    tunnel_ip = '10.{}.10.2'.format(octet2)
                    asn = int(ip[5:6])*10
                    interface = iface
                else:
                    network = ip
        for line in sir_str.splitlines():
            if line.startswith('S*'):
                *junk,nexthop = line.split()
        
        ''' Create Spoke router's dictionary for Yaml File '''
        spoke_dict = {'description': 'To_HUB', 'hostname': hostname.split()[1],
                      'tunnel_ip':tunnel_ip, 'network':network, 'asn':asn, 
                      'interface':interface, 'nexthop':nexthop}

        ''' Create Hub router's  dictionary for Yaml File '''
        as_number = int(str(octet2)[-1])*10
        hub_dict = {'Spoke_Ip': Spoke_Ip,
                    'tunnel_ip': tunnel_ip,
                    'as_number': as_number}
        tk.messagebox.showinfo(message='Finalizing configuration ...')
        return spoke_dict, hub_dict, bgp_dict
 
    def cfg_compile(self):
        spoke_cfg = []    # define final config list for Spoke
        hub_cfg = []      # define final config list for Hub
        [spoke_cfg.append(line) for line in self.result1.splitlines()] # Spoke final configuration
        [hub_cfg.append(line) for line in self.result2.splitlines()]   # Hub final configuration  
        self.cfg_list = [hub_cfg, spoke_cfg]
        return self.cfg_list 
       
class Files_Constructor():
    def __init__(self, yml_file_dict):
         self.yml_file_dict = yml_file_dict
            
    def constructor(self, file_dir, file_name):
        try:
            self.myloader = FileSystemLoader(file_dir)
            self.env = Environment(loader=self.myloader, trim_blocks=True, lstrip_blocks=True)
            self.template = self.env.get_template(file_name)
            self.var_dict = yaml.load(open(self.yml_file_dict), Loader = yaml.FullLoader)
            self.output = self.template.render(self.var_dict)
        except Exception as err:
            messagebox.showerror(title="Yaml error", message=err)
        return self.output

    def create_yaml_file(self, row_data, arg):
        try:
            with open(self.yml_file_dict, arg) as f:
                yaml.dump(row_data, f, default_flow_style=False)
        except FileNotFoundError as err:
            result = mesagebox.showerror(title='Yaml File is missing', message=err)
            self.root.destroy()

def main():
    mainframe = MainFrame()

main()





