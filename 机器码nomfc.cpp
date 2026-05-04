#include <windows.h>
#include <iphlpapi.h>
#include <stdio.h>
#include <string>
#include <vector>
#include <wincrypt.h>
#include <sstream>
#include <iomanip>
#include <iostream>

#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "crypt32.lib")

// 计算MD5哈希
std::string CalculateMD5(const std::string& data) {
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    BYTE rgbHash[16];
    DWORD cbHash = 16;
    CHAR rgbDigits[] = "0123456789ABCDEF";
    std::string strHash;

    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        return "";
    }

    if (!CryptCreateHash(hProv, CALG_MD5, 0, 0, &hHash)) {
        CryptReleaseContext(hProv, 0);
        return "";
    }

    if (!CryptHashData(hHash, (const BYTE*)data.c_str(), data.length(), 0)) {
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

    return strHash.substr(8, 16);
}

// 获取MAC地址
std::string GetMacAddress() {
    PIP_ADAPTER_INFO pAdapterInfo;
    PIP_ADAPTER_INFO pAdapter = NULL;
    DWORD dwRetVal = 0;
    std::string macAddress;

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
                        macAddress += "-";
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

// 从注册表读取字符串值
std::string ReadRegistryString(HKEY hKey, const std::string& subKey, const std::string& valueName, REGSAM samDesired) {
    HKEY hOpenedKey;
    DWORD dwType = 0;
    DWORD dwSize = 0;
    std::string result;

    if (RegOpenKeyExA(hKey, subKey.c_str(), 0, samDesired, &hOpenedKey) == ERROR_SUCCESS) {
        if (RegQueryValueExA(hOpenedKey, valueName.c_str(), NULL, &dwType, NULL, &dwSize) == ERROR_SUCCESS && dwType == REG_SZ) {
            std::vector<char> buffer(dwSize + 1);
            if (RegQueryValueExA(hOpenedKey, valueName.c_str(), NULL, &dwType, (LPBYTE)buffer.data(), &dwSize) == ERROR_SUCCESS) {
                buffer[dwSize] = '\0';
                result = buffer.data();
            }
        }
        RegCloseKey(hOpenedKey);
    }

    return result;
}

// 生成机器码
std::string GenerateMachineCode() {
    std::string data;
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
    std::string macAddress = GetMacAddress();
    
    // 计算数据MD5
    std::string dataMD5 = CalculateMD5(data);
    
    std::cout << macAddress << std::endl;

    // 计算MAC地址MD5
    std::string macMD5 = CalculateMD5(macAddress);
    
    // 组合最终机器码
    std::string machineCode = dataMD5 + "|" + macMD5;
    
    return machineCode;
}

int main() {
    printf("正在生成机器码...\n");
    
    std::string machineCode = GenerateMachineCode();
    
    if (machineCode.empty()) {
        printf("生成机器码失败！\n");
        return 1;
    }
    
    printf("机器码: %s\n", machineCode.c_str());
    printf("\n按任意键退出...");
    getchar();
    
    return 0;
}