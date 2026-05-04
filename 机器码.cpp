#include <windows.h>
#include <iphlpapi.h>
#include <stdio.h>
#include <string.h>
#include <wincrypt.h>
#include <atlstr.h>

#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "crypt32.lib")

// MD5哈希计算函数
CStringA CalculateMD5(const BYTE* data, DWORD length) {
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    BYTE rgbHash[16];
    DWORD cbHash = 16;
    CHAR rgbDigits[] = "0123456789abcdef";
    CStringA strHash;

    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        return "";
    }

    if (!CryptCreateHash(hProv, CALG_MD5, 0, 0, &hHash)) {
        CryptReleaseContext(hProv, 0);
        return "";
    }

    if (!CryptHashData(hHash, data, length, 0)) {
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return "";
    }

    if (CryptGetHashParam(hHash, HP_HASHVAL, rgbHash, &cbHash, 0)) {
        for (DWORD i = 0; i < cbHash; i++) {
            char buf[3];
            sprintf_s(buf, sizeof(buf), "%c%c", rgbDigits[rgbHash[i] >> 4], rgbDigits[rgbHash[i] & 0xf]);
            strHash += buf;
        }
    }

    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);

    return strHash;
}

// 获取MAC地址
CStringA GetMacAddress() {
    PIP_ADAPTER_INFO pAdapterInfo;
    PIP_ADAPTER_INFO pAdapter = NULL;
    DWORD dwRetVal = 0;
    CStringA macAddress;

    ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);
    pAdapterInfo = (IP_ADAPTER_INFO*)malloc(sizeof(IP_ADAPTER_INFO));
    if (pAdapterInfo == NULL) {
        return "";
    }

    if (GetAdaptersInfo(pAdapterInfo, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW) {
        free(pAdapterInfo);
        pAdapterInfo = (IP_ADAPTER_INFO*)malloc(ulOutBufLen);
        if (pAdapterInfo == NULL) {
            return "";
        }
    }

    if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == NO_ERROR) {
        pAdapter = pAdapterInfo;
        while (pAdapter) {
            // 跳过回环适配器
            if (pAdapter->Type != MIB_IF_TYPE_LOOPBACK && pAdapter->AddressLength > 0) {
                for (UINT i = 0; i < pAdapter->AddressLength; i++) {
                    char buf[3];
                    sprintf_s(buf, sizeof(buf), "%02X", pAdapter->Address[i]);
                    macAddress += buf;
                    if (i < (pAdapter->AddressLength - 1)) {
                        macAddress += ":";
                    }
                }
                break;
            }
            pAdapter = pAdapter->Next;
        }
    }

    if (pAdapterInfo) {
        free(pAdapterInfo);
    }

    return macAddress;
}

// 从注册表读取值
CStringA ReadRegistryString(HKEY hKey, LPCSTR subKey, LPCSTR valueName, REGSAM samDesired) {
    HKEY hOpenedKey;
    DWORD dwType = 0;
    DWORD dwSize = 0;
    CStringA result;

    if (RegOpenKeyExA(hKey, subKey, 0, samDesired, &hOpenedKey) == ERROR_SUCCESS) {
        if (RegQueryValueExA(hOpenedKey, valueName, NULL, &dwType, NULL, &dwSize) == ERROR_SUCCESS && dwType == REG_SZ) {
            char* buffer = new char[dwSize + 1];
            if (RegQueryValueExA(hOpenedKey, valueName, NULL, &dwType, (LPBYTE)buffer, &dwSize) == ERROR_SUCCESS) {
                buffer[dwSize] = '\0';
                result = buffer;
            }
            delete[] buffer;
        }
        RegCloseKey(hOpenedKey);
    }

    return result;
}

// 生成机器码
CStringA GenerateMachineCode() {
    CStringA data;
    SYSTEM_INFO systemInfo;
    REGSAM samDesired = KEY_READ;

    // 获取系统信息
    GetSystemInfo(&systemInfo);
    if (systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64 || 
        systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_IA64) {
        samDesired |= KEY_WOW64_64KEY;
    } else {
        samDesired |= KEY_WOW64_32KEY;
    }

    // 从注册表读取信息
    data += ReadRegistryString(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "ProductId", samDesired);
    data += ReadRegistryString(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", "MachineGuid", samDesired);
    data += ReadRegistryString(HKEY_LOCAL_MACHINE, "SOFTWARE\\ETSKey", "InstallDate", samDesired);

    // 获取MAC地址
    CStringA macAddress = GetMacAddress();
    
    // 计算数据MD5
    CStringA dataMD5 = CalculateMD5((const BYTE*)(LPCSTR)data, data.GetLength());
    
    // 计算MAC地址MD5
    CStringA macMD5 = CalculateMD5((const BYTE*)(LPCSTR)macAddress, macAddress.GetLength());
    
    // 组合最终机器码
    CStringA machineCode;
    machineCode.Format("%s|%s", dataMD5, macMD5);
    
    return machineCode;
}

int main() {
    printf("正在生成机器码...\n");
    
    CStringA machineCode = GenerateMachineCode();
    
    if (machineCode.IsEmpty()) {
        printf("生成机器码失败！\n");
        return 1;
    }
    
    printf("机器码: %s\n", machineCode.GetString());
    printf("\n按任意键退出...");
    getchar();
    
    return 0;
}