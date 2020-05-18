import yaml
import netmiko
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
import sys
import ipaddress
import threading
from threading import Thread
from jinja2 import FileSystemLoader,Environment
from queue import Queue
import time 
from datetime import datetime
from operator import itemgetter
from threaded_ssh import send_config, threads_conn
from pprint import pprint
import logging


logger = logging.getLogger("MyLog")
logging.getLogger('paramiko').setLevel(logging.WARNING)
formatter = logging.Formatter('%(threadName)s: %(message)s at %(asctime)s',
                              datefmt='%H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)

HUB_IP = '10.1.1.1'
SPOKE_IP = '10.102.10.2'
##HUB_IP = input('#Enter HUB device ip address:  ')
##SPOKE_IP = input('#Enter Spoke device ip address:  ')
COMMAND_LIST = [
        ('show run | s bgp'),
        ('show ip route',
         'show ip interface brief',
         'show run | include hostname'),]
 #open file with device dictionary
with open('/home/elil/Yml/devices.yml') as f:
    devices = yaml.load(f, Loader= yaml.FullLoader)
        
################################################################################################


class Files_Constructor():
    def __init__(self, yml_file_dict):
         self.yml_file_dict = yml_file_dict
            
    def constructor(self, file_dir, file_name):
        self.myloader = FileSystemLoader(file_dir)
        self.env = Environment(loader=self.myloader, trim_blocks=True, lstrip_blocks=True)
        self.template = self.env.get_template(file_name)
        self.var_dict = yaml.load(open(self.yml_file_dict), Loader = yaml.FullLoader)
        self.output = self.template.render(self.var_dict)
        return self.output

    def create_yaml_file(self, row_data, arg):
        try:
            with open(self.yml_file_dict, arg) as f:
                yaml.dump(row_data, f, default_flow_style=False)
        except FileNotFoundError as e:
            print(e)

'''Main  Class. Connects to devices and returns configuration'''
class Threads(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
               
    '''Core Function...'''
    def netmiko_ssh(self,args):
        ssh = ConnectHandler(**args)
        def send_show(*command):
            return ssh.send_command(*command)    
        return send_show
    
def config_collector(params,commands):
    global mq_dict
    queue = Queue()
    th = Threads()   # Initiate Thread class
    th.start()
    for device,command in zip(params,commands):
        try:
            logger.info('## {} is connecting to device {}...'.format(th.name, device["ip"]))
            Session = th.netmiko_ssh(device)         # connects to device
            print('## Obtaining Device Configuration...')
            if type(command) == str:
                queue.put(Session(command))          # gets device configuration
            else:
                for cfg in command:
                    queue.put(Session(cfg))           # gets device configuration
            th.join()                                 # finish thread execution
            print(f'## {th.name} ended...')
        except  NetMikoAuthenticationException as err:
            tk.messagebox,asqyescancel(message=err)
        except  NetMikoTimeoutException as err:
            tk.messagebox,asqyescancel(message=err)
            
    _value_list = []                ## define values list
    _key_list = ['hub_bgp_list', 'sir_str' , 'sib_str', 'hostname'] ## define keys list
    while not queue.empty():
        _value_list.append(queue.get(timeout=2))

    mq_dict = dict(zip(_key_list,_value_list))                       ## define intermediate dict               
    return mq_dict    
        
def config_parser():
    global  hub_dict, spoke_dict, bgp_dict, ip, octet2, interface, tunnel_ip, iface, network  ## define global variables for YAML file 
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
        if (ip != 'unassigned' and  (status and proto == 'up')) and ('Loop' not in iface):
            octet2 = int(ip[3:6])+100
##          tunnel_ip = ip.replace(ip[3:6],str(octet2))
            tunnel_ip = '10.{}.10.1'.format(octet2)
            asn = int(ip[5:6])*10
            interface = iface
        else:
            network = ip
    for line in sir_str.splitlines():
        if line.startswith('S*'):
            *junk,nexthop = line.split()
    
    ''' Create Spoke dictionary for Yaml File '''
    spoke_dict = {'description': 'To_HUB',
                  'hostname': hostname.split()[1],
                  'tunnel_ip':tunnel_ip,
                  'network':network,
                  'interface':interface,
                  'asn':asn,
                  'nexthop':nexthop}

    ''' Create Hub dictionary for Yaml File '''
    as_number = int(SPOKE_IP.split('.')[1][2])*10    
    hub_dict = {'SPOKE_IP': SPOKE_IP,
                'tunnel_ip': tunnel_ip,
                'as_number': as_number}
    print('## Finalizing configuration...')
    return spoke_dict, hub_dict, bgp_dict, octet2, ip

if __name__ == '__main__':
    
    config_collector(devices, COMMAND_LIST)
    config_parser()
    spoke_jinja_cfg = Files_Constructor(r'/home/elil/Yml/SPOKE_DICT.yml')
    print("stage1")
    hub_jinja_cfg = Files_Constructor(r'/home/elil/Yml/HUB_DICT.yml')
    print("stage1.5")
    result1 = spoke_jinja_cfg.constructor(r"/home/elil/Templates/", r'child_spoke_config_j2')
    print("stage2")
    result2 = hub_jinja_cfg.constructor(r"/home/elil/Templates/", r'hub_config_j2')
    print("stage3")
    spoke_jinja_cfg.create_yaml_file(bgp_dict, 'w')
    print("stage4")
    spoke_jinja_cfg.create_yaml_file(spoke_dict, 'a')
    print("stage5")
    hub_jinja_cfg.create_yaml_file(hub_dict, 'w')
    print("stage6")
    
    spoke_cfg = []                     ## define final config list for SPOKE
    hub_cfg = []                       ## define final config list for HUB
    [spoke_cfg.append(line) for line in result1.splitlines()] # Spoke final configuration
    print("stage7")
    [hub_cfg.append(line) for line in result2.splitlines()]   # Hub final configuration
    print("stage8")
    cfg_list = [hub_cfg, spoke_cfg]
    threads_conn(send_config, devices, 2, cfg_list)
##    print(cfg_list)

    
