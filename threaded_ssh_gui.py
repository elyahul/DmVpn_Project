from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import sys
from itertools import repeat
import tkinter as tk
from tkinter import messagebox
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
import yaml
from contracts import contract

@contract(cfg = 'str[>0]', kwargs = dict)
def send_show(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
        result = ssh.send_command(cfg)
        return result

@contract(cfg = 'list[>0]', kwargs = dict)
def send_config(kwargs, cfg):
    with ConnectHandler(**kwargs) as ssh:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
        result = ssh.send_config_set(cfg)
    return result

def threads_conn(foo, device_list, limit, cfg_list):
    global output_list
    output_list = []
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = []
        for device,cfg in zip(device_list, cfg_list) :
            futures.append(executor.submit(foo, device, cfg))
            messagebox.showinfo(message=f'Finalizing configuration tasks for device {device["ip"]} ...')
        for future in as_completed(futures):
            try:
                output_list.append(future.result())
            except NetMikoAuthenticationException as err:
                messagebox.showerror(message=future.exception())
        return output_list

    
