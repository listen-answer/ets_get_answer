#include <windows.h>
#include <wincrypt.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <iomanip>
#include <sstream>

#pragma comment(lib, "crypt32.lib")

// 计算数据的MD5哈希值
std::vector<BYTE> CalculateMD5(const BYTE* data, DWORD data_len) {
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    DWORD hash_len = 16;
    std::vector<BYTE> hash(hash_len);

    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        throw std::runtime_error("CryptAcquireContext failed");
    }
    
    if (!CryptCreateHash(hProv, CALG_MD5, 0, 0, &hHash)) {
        CryptReleaseContext(hProv, 0);
        throw std::runtime_error("CryptCreateHash failed");
    }
    
    if (!CryptHashData(hHash, data, data_len, 0)) {
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        throw std::runtime_error("CryptHashData failed");
    }
    
    if (!CryptGetHashParam(hHash, HP_HASHVAL, hash.data(), &hash_len, 0)) {
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        throw std::runtime_error("CryptGetHashParam failed");
    }
    
    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);
    return hash;
}

// 二进制数据转十六进制字符串
std::string BytesToHexString(const BYTE* data, size_t len) {
    std::ostringstream oss;
    oss << std::hex << std::uppercase << std::setfill('0');
    for (size_t i = 0; i < len; ++i) {
        oss << std::setw(2) << static_cast<unsigned>(data[i]);
    }
    return oss.str();
}

// 生成压缩包密码
std::string GenerateZipPassword(const std::vector<BYTE>& tailData) {
    const size_t FOOTER_SIZE = 336;
    if (tailData.size() < FOOTER_SIZE) {
        throw std::runtime_error("Tail data too small");
    }

    // 指向尾部数据的起始位置
    const BYTE* footer = tailData.data() + tailData.size() - FOOTER_SIZE;

    // 验证签名 (MSTCHINA 或 EPLAT)
    bool validSignature = 
        (memcmp(footer, "MSTCHINA", 8) == 0) || 
        (memcmp(footer + 144, "EPLAT", 5) == 0);
    
    if (!validSignature) {
        throw std::runtime_error("Invalid file signature");
    }

    // 提取128字节种子数据 (偏移16-143)
    std::vector<BYTE> seed(footer + 16, footer + 16 + 128);

    // 第一重MD5: 计算种子数据的MD5
    auto firstMD5 = CalculateMD5(seed.data(), static_cast<DWORD>(seed.size()));
    std::string firstHex = BytesToHexString(firstMD5.data(), firstMD5.size());

    // 第二重MD5: 计算第一重结果的十六进制字符串的MD5
    auto secondMD5 = CalculateMD5(
        reinterpret_cast<const BYTE*>(firstHex.c_str()), 
        static_cast<DWORD>(firstHex.size())
    );
    std::string secondHex = BytesToHexString(secondMD5.data(), secondMD5.size());

    // 拼接最终密码 (64字符)
    return firstHex + secondHex;
}

int main() {
    try {
        // 读取提供的尾部数据文件 (1000字节)
        std::ifstream file("d214a30f98fda66f46ee5f6fa5017751.zip", std::ios::binary);
        if (!file) {
            std::cerr << "无法打开文件 d214a30f98fda66f46ee5f6fa5017751.zip" << std::endl;
            return 1;
        }
        
        file.seekg(0, std::ios::end);
        size_t size = file.tellg();
        file.seekg(0, std::ios::beg);
        
        std::vector<BYTE> tailData(size);
        file.read(reinterpret_cast<char*>(tailData.data()), size);
        file.close();

        // 生成密码
        std::string password = GenerateZipPassword(tailData);
        
        // 输出结果
        std::cout << "生成的密码: " << password << std::endl;

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
}