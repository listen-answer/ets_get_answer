import hashlib
import winreg
import ctypes
from ctypes import wintypes
import socket
import struct
import subprocess
import re

def calculate_md5(data):
    """计算字符串的MD5哈希值"""
    md5_hash = hashlib.md5(data.encode('utf-8')).hexdigest().upper()
    return md5_hash[8:24]  # 取中间16个字符

def get_mac_address():
    """获取第一个非回环接口的MAC地址"""
    try:
        # 使用ipconfig命令获取MAC地址
        output = subprocess.check_output("ipconfig /all", shell=True, text=True)
        
        # 查找物理适配器的MAC地址
        patterns = [
            r"物理地址[\. ]*: ([\w-]+)",
            r"Physical Address[\. ]*: ([\w-]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for mac in matches:
                if mac != "00-00-00-00-00-00" and not mac.startswith("00-00-00"):  # 排除空地址和虚拟地址
                    return mac.upper()
        
        return ""
    except:
        return ""

def read_registry_string(hkey, subkey, value_name, sam_desired):
    """读取注册表字符串值"""
    try:
        key_handle = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ | sam_desired)
        value, regtype = winreg.QueryValueEx(key_handle, value_name)
        winreg.CloseKey(key_handle)
        
        if regtype == winreg.REG_SZ:
            return str(value)
        else:
            return ""
    except:
        return ""

def generate_machine_code():
    """生成机器码"""
    data = ""
    
    # 确定注册表访问权限
    system_info = ctypes.wintypes.SYSTEM_INFO()
    ctypes.windll.kernel32.GetSystemInfo(ctypes.byref(system_info))
    
    if system_info.wProcessorArchitecture in (9, 6):  # AMD64 or IA64
        sam_desired = winreg.KEY_WOW64_64KEY
    else:
        sam_desired = winreg.KEY_WOW64_32KEY
    
    # 读取注册表值
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", 
                                "ProductId", sam_desired)
    
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\Microsoft\\Cryptography", 
                                "MachineGuid", sam_desired)
    
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\ETSKey", 
                                "InstallDate", sam_desired)
    
    # 获取MAC地址
    mac_address = get_mac_address()
    print(mac_address)
    
    # 计算数据的MD5
    data_md5 = calculate_md5(data)
    
    # 计算MAC地址的MD5
    mac_md5 = calculate_md5(mac_address)
    
    # 组合机器码
    machine_code = data_md5 + "|" + mac_md5
    
    return machine_code

if __name__ == "__main__":
    print("正在生成机器码...")
    
    machine_code = generate_machine_code()
    
    if not machine_code:
        print("生成机器码失败!")
        exit(1)
    
    print("机器码:", machine_code)
    input("\n按任意键退出...")