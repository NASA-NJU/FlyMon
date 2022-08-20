#include "IpAddress.h"
#include <arpa/inet.h>
#include <string.h>
#include <iostream>
#include <string>

Ipv4Address::Ipv4Address(const String& addrStr){
    _addr = inet_addr(addrStr.c_str());
    sscanf(addrStr.c_str(), "%hhu.%hhu.%hhu.%hhu", _addr_bytes, _addr_bytes+1, _addr_bytes+2, _addr_bytes+3);
}
Ipv4Address::Ipv4Address(UINT32_T addrInt)
{
    _addr = addrInt;
    char buffer[INET_ADDRSTRLEN + 1];
    inet_ntop(AF_INET, &addrInt, buffer, sizeof(buffer));
    sscanf(buffer, "%hhu.%hhu.%hhu.%hhu", _addr_bytes, _addr_bytes+1, _addr_bytes+2, _addr_bytes+3);
}

Ipv4Address::Ipv4Address(const Ipv4Address& addr){
    _addr = addr._addr;
    _addr_bytes[0] = addr._addr_bytes[0];
    _addr_bytes[1] = addr._addr_bytes[1];
    _addr_bytes[2] = addr._addr_bytes[2];
    _addr_bytes[3] = addr._addr_bytes[3];
}

Ipv4Address::Ipv4Address(const uint8_t* bytes, int len){
    std::string addr_s = std::to_string(*bytes) 
        + "." + std::to_string(*(bytes + 1))
        + "." + std::to_string(*(bytes + 2))
        + "." + std::to_string(*(bytes + 3));
    _addr = inet_addr(addr_s.c_str());
    _addr_bytes[0] = *bytes;
    _addr_bytes[1] = *(bytes+1);
    _addr_bytes[2] = *(bytes+2);
    _addr_bytes[3] = *(bytes+3);
}

bool Ipv4Address::isValid()const{
    return _addr != INADDR_NONE;
}
String Ipv4Address::getAddrStr()const{
    if (_addr == INADDR_NONE)
        return String("<invalid addr>");
    struct in_addr addr;
    memcpy(&addr, &_addr, 4); 
    return String(inet_ntoa(addr));
}

UINT32_T Ipv4Address::getAddrVal()const{
    return _addr;
}

const uint8_t*  Ipv4Address::getAddrBytes()const{
    return (const uint8_t*)_addr_bytes;
}

Ipv4Address Ipv4Address::mask(const Ipv4Address& mask)const{
    return Ipv4Address(_addr & mask._addr);
}
bool Ipv4Address::operator<(const Ipv4Address& another)const
{
    return _addr < another._addr;
}
bool Ipv4Address::operator!=(const Ipv4Address& another)const
{
    return _addr != another._addr;
}
bool Ipv4Address::operator==(const Ipv4Address& another)const
{
    return _addr == another._addr;
}