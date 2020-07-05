import tkinter as tk
import sys
from tkinter import ttk
import ipaddress
import time
from tkinter import messagebox
from tkinter import simpledialog
import yaml
import netmiko
import paramiko
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
import pdb
import re

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
        self.txtvar.set('Please Input Hub & Spoke Ip Addresses')
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
        
    @staticmethod                       # function to check ip address sanity
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

    def submit_ip(self, event=None):                           # this function defines behavier when "submit_ip" button is pressed
        try:
            
            global Hub_Ip, Spoke_Ip
            Hub_Ip = self.hub_entry.get()                      # read Hub ip address
            Spoke_Ip = self.spoke_entry.get()                  # read Spoke ip address
            
            if (self.check_ip(Hub_Ip) == False) or (self.check_ip(Spoke_Ip) == False):  # Check for HUB and Spoke ip address sanity
                self.clear_entry()
                self.txtvar.set("Please Try Again. Input the correct Ip's")
            elif Hub_Ip == Spoke_Ip:                                                    
                self.clear_entry()     
                self.txtvar.set("Please Try Again. Same Ip's not allowed")
            else:
                self.clear_entry()
                self.txtvar.set("Ip's are accepted. Starting application ...")
                self.main_foo()
        except AttributeError as err:                           # exception when attribute is not found in class object 
            print("Error in program execution !!!", '\n',err)
        except paramiko.buffered_pipe.PipeTimeout as err:       # catch timeout exception 
            print(err)
        except NetMikoTimeoutException as err:
            print(err)
        except OSError as err:
            print("Error in Netmiko Module !!!", '\n',err)
        return Hub_Ip, Spoke_Ip
        
    def main_foo(self):
        COUNT = 0
        global flag
        flag = True
        key_list=['device_type', 'ip', 'username', 'password']
        listglobal=['cisco_ios', 'elil', 'cisco']
        listglobal.insert(1, Hub_Ip)
        listglobal1=['cisco_ios', 'elil', 'cisco']
        listglobal1.insert(1, Spoke_Ip)
        device1 = dict(zip(key_list,listglobal))    # define dictionary for Netmiko (**kwarg )
        device2 = dict(zip(key_list,listglobal1))
        devices=[device1,device2]                     
        result = tk.messagebox.askyesno(message="Ip's are Accepted\n  Continue?")
        if result == False:                                    # exit program if "No" button pressed 
            self.message.grid(row=1, columnspan=2, padx=80, pady=5)
            self.txtvar.set(' Exiting  application ..')
            self.root.after(2000, self.root.destroy)
              
        for device in devices:                                 # check connectivity to devices
            reachable = self.pingable(device["ip"])
            COUNT += reachable
        if COUNT == 0:                                         # if all devices are pingable then proceed
            self.config_collector(devices, COMMAND_LIST)       # collects data from devices

            for item in value_list:
                if 'Invalid' in item:                                             # if got an output error ...
                    tk.messagebox.showerror(title="Fatal Error", message="Wrong commands executed..\n terminating programm !!!")
                    self.destroy_self()
                    sys.exit()
                elif (len(item) == 0):                                            # if could not get proper configuration ...
                    flag = False
                    self.config_collector(devices, COMMAND_LIST)                  # then recollect data from devices
                else:
                    flag = True 
            self.config_parser()                                                  # parse configuration 
            spoke_jinja_cfg = Files_Constructor(r'/home/elil/Yml/SPOKE_DICT.yml') # Instantiate Class
            hub_jinja_cfg = Files_Constructor(r'/home/elil/Yml/HUB_DICT.yml')     # Instantiate Class
            spoke_jinja_cfg.create_yaml_file(bgp_dict, 'w')    # Configuring YAML file for Spoke
            spoke_jinja_cfg.create_yaml_file(spoke_dict, 'a')  # Configuring YAML file for Spoke
            hub_jinja_cfg.create_yaml_file(hub_dict, 'w')      # Configuring YAML file for Hub
            self.result1 = spoke_jinja_cfg.constructor(r"/home/elil/Templates/", r'child_spoke_config.j2')
            self.result2 = hub_jinja_cfg.constructor(r"/home/elil/Templates/", r'hub_config.j2')
            self.cfg_compile()                                 # finalizing configuration of devices
            pdb.set_trace()
            threads_conn(send_config, devices, 2, self.cfg_list)    # send configuration to devices
            proceed = messagebox.askyesno(message='Spoke device is added to DmVpn cloud. Would you like to configure next device ?')
            if proceed == True:
                self.root.lift()                          
                self.root.focus_force()
                self.clear_entry()
                self.txtvar.set('Please Input Hub & Spoke Ip Addresses')
            else:
                self.root.destroy()
        else:                                          # if one of the devices are unreachable then proceed .. 
            self.clear_entry()
            self.retry = tk.messagebox.askretrycancel(message="Retry?  Quit Application?")
            if self.retry == True:                     # if pressed "retry" button
                self.clear_entry()                     # clear input 
                self.txtvar.set("Check devices reachability before input")
            else:                                      # if pressed "cancel" button
                self.root.destroy()                    # terminate programm
        return Hub_Ip, Spoke_Ip, flag
    
    def netmiko_ssh(self, args):                       # main function for ssh connection 
        self.ssh = ConnectHandler(**args)
        def send_show(command):
            return self.ssh.send_command(command)    
        return send_show
        
    def config_collector(self,params,commands):        # funtion collects cfg data from devices
        self.root.iconify()
        global mq_dict, value_list
        queue = Queue()
        for device,command in zip(params,commands):
            try:
                if flag == True:
                    self.result=tk.messagebox.askokcancel(message=f'Procced with connection to device {device["ip"]} ?')
                else:
                    self.result=tk.messagebox.askokcancel(message=f'ReCollect device {device["ip"]} configuration ?')
                if self.result==False:                  # exit program if "Cancel" button pressed
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
                
        mq_dict = {}                                       # zeroize dictionary
        value_list = []                                   
        key_list = ['hub_bgp_list', 'sir_str' ,'sib_str', 'hostname'] 
        try:
            while not queue.empty():
                 value_list.append(queue.get(timeout=2))   # get data from the queue
        except queue.Empty as err:
            print(err)
        mq_dict = dict(zip(key_list, value_list))          # configure intermediate dict               
        return mq_dict, value_list

    def config_parser(self):
        global  hub_dict, spoke_dict, bgp_dict             # define global variables for Yaml file 
        bgp_neigbors = []                                  # list of Hub current BGP Neigbors
        bgp_dict = {'bgp':bgp_neigbors}                    # Bgp neigbors dictionary(For Yaml)
        for key,value in mq_dict.items():
            globals().update(mq_dict)

        ''' Get Data from Hub Configuration and create Yaml File '''
        ([bgp_neigbors.append(line) for line in mq_dict['hub_bgp_list'].splitlines()
          if ('neighbor' and 'remote-as') in line])

        ''' Get Data from Spoke Configuration  and create dictionary for Yaml File '''
        for line in sib_str.splitlines()[1:]:
            iface,ip,*_,status,proto = line.split()
            if (ip != 'unassigned' and  (status and proto == 'up')):
                if not (iface.startswith('L') or iface.startswith('T')):
                    tunnel_ip = ip.replace('10.1','10.2',1)                     # Gre Tunnel ip address
                    asn = int(ip[5:6])*10                                       
                    interface = iface                                           # get source interface for Gre Tunnel
                else:
                    if not iface.startswith('T'):                              
                        network = ip                                            # get local network to advertise through BGP 
        for line in sir_str.splitlines():
            if line.startswith('S*'):
                *junk,nexthop = line.split()                                    # extract nexthop ip address
        spoke_network_prefix = ipaddress.ip_network(Spoke_Ip +'/30', strict=False)     # get network address from "Spoke_Ip"
        row_network = re.match("(\S+)/", spoke_network_prefix.with_prefixlen)          # get network address from "Spoke_Ip"
        spoke_subnet = row_network.group(1)                                            # get network address from "Spoke_Ip"
        
        ''' Create Spoke router's dictionary for Yaml File '''
        spoke_dict = {'description': 'To_HUB', 'hostname': hostname.split()[1],
                      'tunnel_ip': tunnel_ip, 'network': network, 'as_number': asn, 
                      'interface': interface, 'nexthop': nexthop}

        ''' Create Hub router's  dictionary for Yaml File '''
        hub_dict = {'spoke_subnet': spoke_subnet,
                    'tunnel_ip': tunnel_ip,
                    'as_number': asn}
        tk.messagebox.showinfo(message='Finalizing configuration ...')
        return spoke_dict, hub_dict, bgp_dict
 
    def cfg_compile(self):
        global spoke_cfg
        global hub_cfg
        spoke_cfg = []    # define final config list for Spoke
        hub_cfg = []      # define final config list for Hub
        [spoke_cfg.append(line) for line in self.result1.splitlines()] # Spoke final configuration
        [hub_cfg.append(line) for line in self.result2.splitlines()]   # Hub final configuration  
        self.cfg_list = [hub_cfg, spoke_cfg]
        return self.cfg_list , spoke_cfg, hub_cfg
       
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
    

if __name__ == '__main__':
    main()
    





