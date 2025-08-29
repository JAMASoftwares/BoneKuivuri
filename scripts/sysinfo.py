import platform
import psutil
from cpuinfo import get_cpu_info


"""
Scale bytes to its proper format
e.g:
    1253656 => '1.20MB'
    1253656678 => '1.17GB'
"""
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_cpu_info_as_dict():
    # Get OS information
    os_name = platform.system()
    os_version = platform.release()
    # Get CPU information
    cpu_name = get_cpu_info()['brand_raw']
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_max_frequency = psutil.cpu_freq().max
    # Get Memory information
    memory_info = psutil.virtual_memory()
    total_memory_mb = get_size(bytes=memory_info.total)

    # Construct the information dictionary
    system_info = {
        "os_name": os_name,
        "os_version": os_version,
        "cpu": {
            "name": cpu_name,
            "cores": cpu_cores,
            "threads": cpu_threads,
            "max_freq_mhz": cpu_max_frequency,
            "total_memory_mb": total_memory_mb,
        }
    }

    return system_info


def get_disk_info_as_dict():
    sys_data = {}
    par_data = {}
    # Disk Information
    # Get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        par_data['device'] = partition.device
        par_data['mount_point'] = partition.mountpoint
        par_data['file_system'] = partition.fstype
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        par_data['total_size'] = get_size(partition_usage.total)
        par_data['used'] = get_size(partition_usage.used)
        par_data['free'] = get_size(partition_usage.free)
        par_data['%'] = partition_usage.percent
        sys_data['partition'] = par_data
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    sys_data['total_read'] = get_size(disk_io.read_bytes)
    sys_data['total_write'] = get_size(disk_io.write_bytes)
    
    return sys_data

def get_net_info_as_dict():
    import psutil
    import socket

    net_data = {}
    # Get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface in if_addrs.items():
        interface_name = interface[0]
        if_data = {}
        for address in interface[1]:
            if address.family == socket.AF_INET:
                if_data['ip_address'] = address.address
                if_data['netmask'] = address.netmask
                if_data['broadcast_ip'] = address.broadcast
            elif getattr(psutil, 'AF_LINK', None) is not None and address.family == psutil.AF_LINK:
                if_data['mac_address'] = address.address
            elif hasattr(socket, 'AF_PACKET') and address.family == socket.AF_PACKET:
                if_data['mac_address'] = address.address
        net_data[interface_name] = if_data

    net_io = psutil.net_io_counters()
    net_data['total_bytes_sent'] = get_size(net_io.bytes_sent)
    net_data['total_bytes_received'] = get_size(net_io.bytes_recv)

    #print(net_data)

    return net_data
