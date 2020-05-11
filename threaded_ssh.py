from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import sys
from itertools import repeat
import logging
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
import yaml
from contracts import contract

logging.getLogger('paramiko').setLevel(logging.WARNING)
logging.basicConfig(
    format = '%(threadName)s %(name)s: %(message)s',
    level=logging.INFO)

start_msg = '====> {} Connection: '

@contract(cfg = 'str[>0]', kwargs = dict)
def send_show(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
        logging.info(start_msg.format(datetime.now().time()))
        result = ssh.send_command(cfg)
        return result

@contract(cfg = 'list[>0]', kwargs = dict)
def send_config(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
        logging.info(start_msg.format(datetime.now().time()))
        result = ssh.send_config_set(*cfg)
        return result

def threads_conn(foo, device_list, limit, cfg_list):
    global output_list
    output_list = []
    print(cfg_list)
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = []
        for device,cfg in zip(device_list, cfg_list) :
            futures.append(executor.submit(foo, device, cfg))
        for future in as_completed(futures):
            try:
                output_list.append(future.result())
            except NetMikoAuthenticationException as err:
                print(future.exception())
    return output_list

    
