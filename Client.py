import platform
import os
import psutil
import socket
import uuid
# import GPUtil    Discontinued on python 3.12, using python 3.13.3

from datetime import datetime
import requests
import socketio
import time

sio = socketio.Client()

import pynvml #using pynmvl to help get GPU information

def get_gpu_info():
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_data = {}
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode()
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            gpu_data[f"GPU_{i}"] = {
                "Name": name,
                "Load": f"{util.gpu}%",
                "Free Memory": f"{mem_info.free // (1024 ** 2)}MB",
                "Used Memory": f"{mem_info.used // (1024 ** 2)}MB",
                "Total Memory": f"{mem_info.total // (1024 ** 2)}MB",
                "Temperature": f"{temp} °C"
            }
        pynvml.nvmlShutdown()
        return gpu_data
    except Exception as e:
        return {"GPU": f"Error or not available - {e}"}
    
def has_gpu():
    try:
        pynvml.nvmlInit()
        count = pynvml.nvmlDeviceGetCount()
        pynvml.nvmlShutdown()
        return count > 0
    except:
        return False

def get_size(bytes, suffix="B"):
    # Convert bytes to KB, MB, GB, etc.
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_system_info():
    uname = platform.uname()
    info = {
        "System": uname.system,
        "Node Name": uname.node,
        "Release": uname.release,
        "Version": uname.version,
        "Machine": uname.machine,
        "Processor": uname.processor,
        "Architecture": platform.architecture()[0]
    }
    return info

def get_cpu_info():
    return {
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max Frequency": f"{psutil.cpu_freq().max:.2f} Mhz",
        "Min Frequency": f"{psutil.cpu_freq().min:.2f} Mhz",
        "Current Frequency": f"{psutil.cpu_freq().current:.2f} Mhz",
        "CPU Usage per Core": [f"{x}%" for x in psutil.cpu_percent(percpu=True)],
        "Total CPU Usage": f"{psutil.cpu_percent()}%"
    }

def get_memory_info():
    svmem = psutil.virtual_memory()
    return {
        "Total": get_size(svmem.total),
        "Available": get_size(svmem.available),
        "Used": get_size(svmem.used),
        "Percentage": f"{svmem.percent}%"
    }

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        disk_info[partition.device] = {
            "Mountpoint": partition.mountpoint,
            "File system type": partition.fstype,
            "Total Size": get_size(usage.total),
            "Used": get_size(usage.used),
            "Free": get_size(usage.free),
            "Percentage": f"{usage.percent}%"
        }
    return disk_info

def get_network_info():
    net_io = psutil.net_io_counters()
    addrs = psutil.net_if_addrs()
    net_info = {
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "Total Sent": get_size(net_io.bytes_sent),
        "Total Received": get_size(net_io.bytes_recv),
        "Interfaces": {}
    }
    for interface_name, interface_addresses in addrs.items():
        net_info["Interfaces"][interface_name] = []
        for address in interface_addresses:
            addr_data = {}
            if str(address.family) == 'AddressFamily.AF_INET':
                addr_data["IP"] = address.address
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                addr_data["MAC"] = address.address
            if addr_data:
                net_info["Interfaces"][interface_name].append(addr_data)
    return net_info

def get_battery_info():
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            return {
                "Percentage": f"{battery.percent}%",
                "Charging": battery.power_plugged,
                "Time Left": f"{battery.secsleft // 60} min" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "N/A"
            }
    return {"Battery": "No battery info available"}

#below is using the GPUtil library and it's deprecated in python 3.12

# def get_gpu_info():
#     try:
#         gpus = GPUtil.getGPUs()
#         gpu_data = {}
#         for i, gpu in enumerate(gpus):
#             gpu_data[f"GPU_{i}"] = {
#                 "Name": gpu.name,
#                 "Load": f"{gpu.load*100:.0f}%",
#                 "Free Memory": f"{gpu.memoryFree}MB",
#                 "Used Memory": f"{gpu.memoryUsed}MB",
#                 "Total Memory": f"{gpu.memoryTotal}MB",
#                 "Temperature": f"{gpu.temperature} °C"
#             }
#         return gpu_data
#     except Exception as e:
#         return {"GPU": f"Error or not available - {e}"}
    

# def has_gpu():
#     gpus = GPUtil.getGPUs()
#     return len(gpus) > 0

def main():
    try:
        sio.connect('http://127.0.0.1:5001/')  # Replace with your Raspberry Pi's IP, or your server's
        print("[SocketIO] Connected to server.")        
        
        while(True):

            system_info = get_system_info()
            cpu_info = get_cpu_info()
            memory_info = get_memory_info()
            disk_info = get_disk_info()
            network_info = get_network_info()
            battery_info = get_battery_info()
            gpu_info = get_gpu_info() if has_gpu() else {"GPU": "No GPU detected"}

            full_data = {       
                "System Info": system_info,
                "CPU Info": cpu_info,
                "Memory Info": memory_info,
                "Disk Info": disk_info,
                "Network Info": network_info,
                "Battery Info": battery_info,
                "GPU Info": gpu_info
            }

            # Emit to server
            sio.emit("system_info", full_data)
            print(f"[SocketIO] Data sent.")

            # Wait before next send
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[!] Monitoring stopped by user.")
    except Exception as e:
        print(f"[SocketIO] Error: {e}")
    finally:
        sio.disconnect()
        print("[SocketIO] Disconnected.")



if __name__ == "__main__":
    main()
