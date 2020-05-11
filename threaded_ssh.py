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

logger = logging.getLogger("MyLog")
logging.getLogger('paramiko').setLevel(logging.WARNING)
formatter = logging.Formatter('## %(levelname)s LOG  %(threadName)s: %(message)s at %(asctime)s',
                              datefmt='%H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)

@contract(cfg = 'str[>0]', kwargs = dict)
def send_show(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
        logger.info('Is connecting to device {}'.format(device["ip"]))
        result = ssh.send_command(cfg)
        return result

@contract(cfg = 'list[>0]', kwargs = dict)
def send_config(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
        logger.info('Is connecting to device {}'.format(device["ip"]))
        result = ssh.send_config_set(cfg)
    return result

def threads_conn(foo, device_list, limit, cfg_list):
    global output_list
    output_list = []
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = []
        for device,cfg in zip(device_list, cfg_list) :
            futures.append(executor.submit(foo, device, cfg))
            logger.info('Device {} configuration is completed at'.format(device["ip"]))
        for future in as_completed(futures):
            try:
                output_list.append(future.result())
            except NetMikoAuthenticationException as err:
                print(future.exception())
        return output_list

    
