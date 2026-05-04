#include <windows.h>
#include <iphlpapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma comment(lib, "iphlpapi.lib")

char __cdecl GetMacAddress(char* outputBuffer)
{
    PIP_ADAPTER_ADDRESSES AdapterAddresses = NULL;
    PIP_ADAPTER_ADDRESSES currentAdapter = NULL;
    char result = 0;
    ULONG size = 15000; // 初始缓冲区大小
    
    // 分配内存
    AdapterAddresses = (PIP_ADAPTER_ADDRESSES)malloc(size);
    if (!AdapterAddresses)
        return 0;
    
    // 获取适配器地址
    DWORD status = GetAdaptersAddresses(AF_UNSPEC, 0, NULL, AdapterAddresses, &size);
    if (status == ERROR_BUFFER_OVERFLOW)
    {
        free(AdapterAddresses);
        AdapterAddresses = (PIP_ADAPTER_ADDRESSES)malloc(size);
        if (!AdapterAddresses)
            return 0;
        
        status = GetAdaptersAddresses(AF_UNSPEC, 0, NULL, AdapterAddresses, &size);
    }
    
    if (status == NO_ERROR)
    {
        // 遍历所有适配器
        for (currentAdapter = AdapterAddresses; currentAdapter != NULL; currentAdapter = currentAdapter->Next)
        {
            // 跳过没有物理地址的适配器
            if (currentAdapter->PhysicalAddressLength == 0)
                continue;
                
            // 只处理以太网适配器（类型为IF_TYPE_ETHERNET_CSMACD）
            if (currentAdapter->IfType == IF_TYPE_ETHERNET_CSMACD && 
                currentAdapter->PhysicalAddressLength == 6)
            {
                // 格式化MAC地址
                sprintf_s(outputBuffer, 18, "%02X-%02X-%02X-%02X-%02X-%02X",
                         currentAdapter->PhysicalAddress[0],
                         currentAdapter->PhysicalAddress[1],
                         currentAdapter->PhysicalAddress[2],
                         currentAdapter->PhysicalAddress[3],
                         currentAdapter->PhysicalAddress[4],
                         currentAdapter->PhysicalAddress[5]);
                
                result = 1;
                break;
            }
        }
    }
    
    free(AdapterAddresses);
    return result;
}

// 测试函数
int main()
{
    char macAddress[18] = {0}; // MAC地址格式: XX-XX-XX-XX-XX-XX (17字符 + 空终止符)
    
    if (GetMacAddress(macAddress))
    {
        printf("MAC Address: %s\n", macAddress);
    }
    else
    {
        printf("Failed to get MAC address.\n");
    }
    
    return 0;
}