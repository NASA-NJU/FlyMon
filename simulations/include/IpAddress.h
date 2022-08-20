#ifndef _IPADDRESS_H_
#define _IPADDRESS_H_

#include <cstring>
#include <string>
#include <memory>

using INT32_T = int;
using INT64_T = long;
using UINT32_T = unsigned int;
using UINT64_T = unsigned long long;

using NODE_ID = unsigned int;
using EVENT_ID = unsigned long long;

using String=std::string;
class Ipv4Address{
public:
    Ipv4Address(const Ipv4Address& addrStr);
    Ipv4Address(const String& addrStr);
    Ipv4Address(UINT32_T addrInt=-1);
    Ipv4Address(const uint8_t* bytes, int len=4);
    bool isValid()const;
    String getAddrStr()const;
    UINT32_T getAddrVal()const;
    const uint8_t*  getAddrBytes()const;
    Ipv4Address mask(const Ipv4Address& mask)const;
    bool operator<(const Ipv4Address& another)const;
    bool operator!=(const Ipv4Address& another)const;
    bool operator==(const Ipv4Address& another)const;
private:
    UINT32_T _addr;
    char _addr_bytes[4];
};

#endif