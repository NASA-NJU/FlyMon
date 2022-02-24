#include "Packet.h"
#include "Packet.h"
#include <cstring>
#include <iostream>
using namespace std;

Packet::Packet(const String& srcAddr, const String& dstAddr, UINT32_T pktSize, const String& msg)
    : _ipv4Src(srcAddr), _ipv4Dst(dstAddr), _pktSize(pktSize), _msg(msg)
{

}
Packet::Packet(const Ipv4Address& srcAddr, const Ipv4Address& dstAddr, UINT32_T pktSize, const String& msg)
    : _ipv4Src(srcAddr), _ipv4Dst(dstAddr), _pktSize(pktSize), _msg(msg)
{

}
Packet::Packet(const char* five_tuple)
    : _ipv4Src((const uint8_t *)five_tuple, 4), _ipv4Dst((const uint8_t *)five_tuple + 4 + 2, 4)
{
    memcpy(_sport, five_tuple + 4, 2);
    memcpy(_dport, five_tuple + 4 + 2 + 4, 2);
    memcpy(_protocol, five_tuple + 4 + 2 + 4 + 2, 1);
}

Ipv4Address Packet::getDstIpAddr()const{
    return _ipv4Dst;
}
Ipv4Address Packet::getSrcIpAddr()const{
    return _ipv4Src;
}

const uint8_t* Packet::getDstIpAddrBytes()const{
    return _ipv4Dst.getAddrBytes();
}
const uint8_t* Packet::getSrcIpAddrBytes()const{
    return _ipv4Src.getAddrBytes();
}
String Packet::getDstIpAddrStr()const{
    return _ipv4Dst.getAddrStr();
}
String Packet::getSrcIpAddrStr()const{
    return _ipv4Src.getAddrStr();
}
UINT32_T Packet::getPktSize()const{
    return _pktSize;
}
String Packet::getMessage()const{
    return _msg;
}
String Packet::toString()const{
    return "Dst:"+getDstIpAddrStr()+" Src:" +getSrcIpAddrStr() + " Size=" + std::to_string(_pktSize);
}