

import requests
import hashlib
import base64
import json
import time

# 全局配置
API_BASE_URL = "https://api.ets100.com"
PID = "grlx"
SECRET_KEY = "555ffbe95ccf4e9535a110170b445ab8"


def generate_fake_hwid():
    """生成伪造的机器码"""
    # 伪造注册表数据
    fake_product_id = "12345-ABCDE-67890-FGHIJ"
    fake_machine_guid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    fake_install_date = "20200101"
    
    data = fake_product_id + fake_machine_guid + fake_install_date
    data_md5 = hashlib.md5(data.encode('utf-8')).hexdigest().upper()[8:24]
    
    # 伪造MAC地址
    fake_mac = "00:11:22:33:44:55"
    mac_md5 = hashlib.md5(fake_mac.encode('utf-8')).hexdigest().upper()[8:24]
    
    return data_md5 + "|" + mac_md5


def generate_real_hwid():
    """生成真实的机器码（参考hwid.py）"""
    import winreg
    import ctypes
    from ctypes import wintypes
    
    class SYSTEM_INFO(ctypes.Structure):
        _fields_ = [
            ("wProcessorArchitecture", wintypes.WORD),
            ("wReserved", wintypes.WORD),
            ("dwPageSize", wintypes.DWORD),
            ("lpMinimumApplicationAddress", ctypes.c_void_p),
            ("lpMaximumApplicationAddress", ctypes.c_void_p),
            ("dwActiveProcessorMask", ctypes.c_void_p),
            ("dwNumberOfProcessors", wintypes.DWORD),
            ("dwProcessorType", wintypes.DWORD),
            ("dwAllocationGranularity", wintypes.DWORD),
            ("wProcessorLevel", wintypes.WORD),
            ("wProcessorRevision", wintypes.WORD)
        ]
    
    def calculate_md5(data):
        md5_hash = hashlib.md5(data.encode('utf-8')).hexdigest().upper()
        return md5_hash[8:24]
    
    def read_registry_string(hkey, subkey, value_name, sam_desired):
        try:
            key_handle = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ | sam_desired)
            value, regtype = winreg.QueryValueEx(key_handle, value_name)
            winreg.CloseKey(key_handle)
            if regtype == winreg.REG_SZ:
                return str(value)
            return ""
        except:
            return ""
    
    system_info = SYSTEM_INFO()
    ctypes.windll.kernel32.GetSystemInfo(ctypes.byref(system_info))
    
    if system_info.wProcessorArchitecture in (9, 6):
        sam_desired = winreg.KEY_WOW64_64KEY
    else:
        sam_desired = winreg.KEY_WOW64_32KEY
    
    data = ""
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", 
                                "ProductId", sam_desired)
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\Microsoft\\Cryptography", 
                                "MachineGuid", sam_desired)
    data += read_registry_string(winreg.HKEY_LOCAL_MACHINE, 
                                "SOFTWARE\\ETSKey", 
                                "InstallDate", sam_desired)
    
    import subprocess, re
    mac_address = ""
    try:
        output = subprocess.check_output("ipconfig /all", shell=True, text=True)
        for pattern in [r"物理地址[\. ]*: ([\w-]+)", r"Physical Address[\. ]*: ([\w-]+)"]:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for mac in matches:
                if mac != "00-00-00-00-00-00" and not mac.startswith("00-00-00"):
                    mac_address = mac.upper()
                    break
    except:
        pass
    
    data_md5 = calculate_md5(data)
    mac_md5 = calculate_md5(mac_address)
    return data_md5 + "|" + mac_md5


def make_signature(content: str, timestamp: int) -> str:
    """生成请求签名"""
    sign_string = f"{PID}{timestamp}{content}{SECRET_KEY}"
    return hashlib.md5(sign_string.encode("utf-8")).hexdigest()


def send_request(endpoint: str, body_data: list, device_code: str) -> dict:
    """发送请求"""
    body_json = json.dumps(body_data, separators=(',', ':'), ensure_ascii=False)
    body_b64 = base64.b64encode(body_json.encode("utf-8")).decode("utf-8")
    timestamp = int(time.time())
    
    headers = {
        "Host": "api.ets100.com",
        "User-Agent": "libcurl-agent/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*"
    }
    
    payload = {
        "body": body_b64,
        "head": {
            "version": "1.0",
            "sign": make_signature(body_b64, timestamp),
            "pid": PID,
            "time": timestamp,
        }
    }
    
    payload_json = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    
    response = requests.post(endpoint, data=payload_json, headers=headers, timeout=30)
    return response.json()


def test_login(phone: str, password: str, use_fake: bool = True) -> dict:
    """测试登录"""
    device_code = generate_fake_hwid() if use_fake else generate_real_hwid()
    
    body_data = [{
        "r": "user/login",
        "params": {
            "sn": "test",
            "phone": phone,
            "password": password,
            "device_code": device_code,
            "device_name": "TEST-PC",
            "version": "3",
            "local_ip": "127.0.0.1",
            "system": "4",
            "global_client_version": "",
            "sign_response": 1,
        }
    }]
    
    return send_request(f"{API_BASE_URL}/user/login", body_data, device_code)


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("伪造机器码登录测试")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("\n使用方法:")
        print("  python test_fake_hwid.py <手机号> <密码>")
        print("\n示例:")
        print("  python test_fake_hwid.py 13800138000 password123")
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    
    # 测试伪造机器码
    print(f"\n[测试1] 使用伪造机器码登录...")
    print(f"  手机号: {phone}")
    print(f"  机器码: {generate_fake_hwid()}")
    
    try:
        result = test_login(phone, password, use_fake=True)
        print(f"\n  返回结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "body" in result and "token" in result[0].get("body", {}):
            print("\n✅ 伪造机器码登录成功！服务器不校验机器码真实性")
        else:
            error_msg = result[0].get("body", {}).get("error", "未知错误")
            print(f"\n❌ 登录失败: {error_msg}")
            print("   这可能意味着服务器校验了机器码")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    
    # 测试真实机器码（仅作为对比）
    try:
        real_hwid = generate_real_hwid()
        print(f"\n[测试2] 使用真实机器码登录（仅对比）...")
        print(f"  机器码: {real_hwid}")
        
        result2 = test_login(phone, password, use_fake=False)
        if "body" in result2 and "token" in result2[0].get("body", {}):
            print("\n✅ 真实机器码登录成功")
        else:
            error_msg = result2[0].get("body", {}).get("error", "未知错误")
            print(f"\n❌ 真实机器码也失败了: {error_msg}")
    except Exception as e:
        print(f"\n⚠️ 真实机器码测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
