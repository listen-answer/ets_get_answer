#include <iostream>
#include <cstring>
#include <iomanip>
#include <cstdint>  // 添加缺失的头文件

// MD5状态结构
struct MD5Context {
    uint32_t state[4];   // A, B, C, D
    uint8_t buffer[64];  // 当前处理块
};

// 字节序转换函数（之前的sub_508D10）
void bytesToDwords(const uint8_t* src, uint32_t* dest, size_t byteCount) {
    for (size_t i = 0; i < byteCount / 4; i++) {
        dest[i] = (static_cast<uint32_t>(src[i*4+3]) << 24) |
                  (static_cast<uint32_t>(src[i*4+2]) << 16) |
                  (static_cast<uint32_t>(src[i*4+1]) << 8) |
                  static_cast<uint32_t>(src[i*4]);
    }
}

// MD5核心计算函数（sub_507B70）
void md5Transform(uint32_t state[4], const uint8_t block[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t x[16];
    
    // 字节序转换
    bytesToDwords(block, x, 64);

    // MD5四轮计算
    #define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32-(n))))
    #define F(x, y, z) (((x) & (y)) | ((~x) & (z)))
    #define G(x, y, z) (((x) & (z)) | ((y) & (~z)))
    #define H(x, y, z) ((x) ^ (y) ^ (z))
    #define I(x, y, z) ((y) ^ ((x) | (~z)))

    // 第一轮
    #define FF(a, b, c, d, x, s, ac) { \
        a += F(b, c, d) + x + ac; \
        a = ROTATE_LEFT(a, s); \
        a += b; \
    }
    
    // 第二轮
    #define GG(a, b, c, d, x, s, ac) { \
        a += G(b, c, d) + x + ac; \
        a = ROTATE_LEFT(a, s); \
        a += b; \
    }
    
    // 第三轮
    #define HH(a, b, c, d, x, s, ac) { \
        a += H(b, c, d) + x + ac; \
        a = ROTATE_LEFT(a, s); \
        a += b; \
    }
    
    // 第四轮
    #define II(a, b, c, d, x, s, ac) { \
        a += I(b, c, d) + x + ac; \
        a = ROTATE_LEFT(a, s); \
        a += b; \
    }

    // 标准MD5计算步骤
    // 这里只展示部分步骤，完整实现需要64步操作
    FF(a, b, c, d, x[0], 7, 0xd76aa478);
    FF(d, a, b, c, x[1], 12, 0xe8c7b756);
    FF(c, d, a, b, x[2], 17, 0x242070db);
    // ... 完整实现需要64个步骤 ...
    II(a, b, c, d, x[0], 6, 0xf4292244);
    II(d, a, b, c, x[7], 10, 0x432aff97);
    // ... 省略其他步骤 ...

    // 更新状态
    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

int main() {
    MD5Context ctx;
    
    // 初始化MD5状态
    ctx.state[0] = 0x67452301;
    ctx.state[1] = 0xEFCDAB89;
    ctx.state[2] = 0x98BADCFE;
    ctx.state[3] = 0x10325476;
    
    // 示例输入数据
    const char* msg = "BiZGs4d0hLVXU4WUM0SlZSVlhCc2xMT0RKbE11VGx1TTQiLCJzeXN0ZW0iOiI0IiwiZ2xvYmFsX2NsaWVudF92ZXJzaW9uIjoiIiwic2lnbl9yZXNwb25zZSI6MX19XQ==555ffbe95ccf4e9535a110170b445ab8";
    memcpy(ctx.buffer, msg, strlen(msg));
    
    // 处理数据块
    md5Transform(ctx.state, ctx.buffer);
    //b988
    // 输出结果
    std::cout << "MD5 Hash: ";
    for (int i = 0; i < 4; i++) {
        std::cout << std::hex << std::setfill('0') << std::setw(8) << ctx.state[i];
    }
    std::cout << std::endl;
    
    return 0;
}