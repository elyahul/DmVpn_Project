import yaml
import netmiko
from netmiko import ConnectHandler
import sys
import ipaddress
import threading
from threading import Thread
from jinja2 import FileSystemLoader,Environment
from queue import Queue
import time
from operator import itemgetter
from threaded_ssh import send_show, threads_conn
from pprint import pprint

HUB_IP = input('#Enter HUB device ip address:  ')
SPOKE_IP = input('#Enter Spoke device ip address:  ')
DEVICES_IP_LIST = [HUB_IP,SPOKE_IP]           
COMMAND_LIST = [
        ('show run | s bgp',),
        ('show ip route',
         'show ip interface brief',
         'show run | include hostname'),]

with open('/home/elil/Yml/devices.yml') as f:
        devices = yaml.load(f, Loader= yaml.FullLoader)

def check_ip(ip):                                           ##Function to chek ip adress sanity
    try:
        ipaddress.ip_address(ip)
    except ValueError as e:
        print('#Wrong Ip Address...',e)
        return False
    
for ip in DEVICES_IP_LIST:
    check_ip(ip)
    
def create_yaml_file(file_path, row_data, arg):
    try:
        with open(file_path, arg) as f:
            yaml.dump(row_data, f, default_flow_style=False)
    except FileNotFoundError as e:
        print(e)

class Jinja_Config_Constructor():
    def __init__(self, file_dir, file_name, data_dir):
        self.file_dir = file_dir
        self.file_name = file_name
        self.data_dir = data_dir
            
    def constructor(self):
        myloader = FileSystemLoader(self.file_dir)
        env = Environment(loader=myloader, trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(self.file_name)
        var_dict = yaml.load(open(self.data_dir), Loader = yaml.FullLoader)
        output = template.render(var_dict)
        return output
    
class Threads(threading.Thread):
    global mq
    mq = Queue()
    
    '''Main Code Class. Connects to devices and returns configuration'''
    def __init__(self):
        threading.Thread.__init__(self)
               
    '''Core Function...'''

    def netmiko_ssh(self,args):
        ssh = ConnectHandler(**args)
        def send_show(*command):
            return ssh.send_command(*command)    
        return send_show
   
    ''' Queue filling function...'''
    
    def queue_producer(self,*arg):
        mq.put(*arg, block=True)
        time.sleep(1)
        return mq
    
def config_collector(params,command):
    global _mq_dict
    global _value_list
                       
    t = Threads()                                                  ## Initiate Thread class
    t.start()
    print(f'## {t.name} started')
    for dev_dict,command in zip(devices,COMMAND_LIST):
        print(f'## Connecting to device {dev_dict["ip"]}...')
        Session  = t.netmiko_ssh(dev_dict)
        print('## Obtaining Device Configuration...')
        if len(command) == 1:
            t.queue_producer(Session(*command))
        else:
            for cfg in command:
                t.queue_producer(Session(cfg))
    t.join()
    print(f'## {t.name} ended')
                
    #''' Here we create dict to store and parse config output from both devices...'''
    _value_list = []                                                 ## define values list
    _key_list = ['hub_bgp_list', 'sir_str' , 'sib_str', 'hostname']  ## define keys list
    x = 0
    while not mq.empty():
        _value_list.append(mq.get(timeout=2))
        pprint(_value_list[x])
        x = x +1
        
    _mq_dict = dict(zip(_key_list,_value_list))                       ## define intermediate dict               
    return _mq_dict    
        
def config_parser():
    global  hub_dict, spoke_dict, bgp_dict  ## define global variables for YAML file 
    bgp_neigbors = []                       ## List of Hub Current BGP Neigbors
    bgp_dict = {'bgp':bgp_neigbors}         ## Bgp Neigbors Dictionary(For Yaml)

    for key,value in _mq_dict.items():
        globals().update(_mq_dict)
        
    ''' Get Data from Hub Configuration and create Yaml File '''

    ([ bgp_neigbors.append(line) for line in hub_bgp_list.splitlines()
      if ('neighbor' and 'remote-as') in line])

    ''' Get Data from Spoke Configuration  and create dictionary for Yaml File '''

    for line in sib_str.splitlines()[2:]:
        iface,ip,*_,status,proto = line.split()
        if (ip != 'unassigned' and  (status and proto == 'up')):
            if not (iface.startswith('L') or iface.startswith('T')):
                octet2 = int(ip[3:6])+100
                tunnel_ip = ip.replace(ip[3:6],str(octet2))
                asn = int(ip[5:6])*10
                #tunnel_ip = '10.{}.10.2'.format(int(ip[3:6])+100)
                interface = iface
            else:
                network = ip
    global nexthop            
    for line in sir_str.splitlines():
        if line.startswith('S*'):
            *junk,nexthop = line.split()
    
    ''' Create Spoke dictionary for Yaml File '''
    global spoke_dict
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
    
    return spoke_dict, hub_dict, bgp_dict

if __name__ == '__main__':
    
    config_collector(devices, COMMAND_LIST)
    config_parser()
    create_yaml_file(r'/home/elil/Yml/SPOKE_DICT.yml', bgp_dict, 'w')
    create_yaml_file(r'/home/elil/Yml/SPOKE_DICT.yml', spoke_dict, 'a')
    create_yaml_file(r'/home/elil/Yml/HUB_DICT.yml', hub_dict, 'w')

    spoke_jinja_cfg = Jinja_Config_Constructor(r'/home/elil/Templates/',
                                               r'child_spoke_config_j2',
                                               r'/home/elil/Yml/SPOKE_DICT.yml')              
    hub_jinja_cfg   = Jinja_Config_Constructor(r'/home/elil/Templates/',
                                               r'hub_config_j2',
                                               r'/home/elil/Yml/HUB_DICT.yml')
    
    spoke_cfg = []                                         ## define final config list for SPOKE
    hub_cfg = []                                           ## define final config list for HUB
    [spoke_cfg.append(line) for line in spoke_jinja_cfg.constructor().splitlines()] # spoke final cfg
    [hub_cfg.append(line) for line in hub_jinja_cfg.constructor().splitlines()]     # hub final cfg
    cfg_list = [spoke_cfg, hub_cfg]
    threads_conn(send_show, devices, 2, cfg_list)




    
