#ifndef _NSPACKET_H_
#define _NSPACKET_H_

#include "IpAddress.h"
//精简化的数据包
class Packet{
public:
    Packet(const String& srcAddr, const String& dstAddr, UINT32_T pktSize, const String& msg="");
    Packet(const Ipv4Address& srcAddr, const Ipv4Address& dstAddr, UINT32_T pktSize, const String& msg="");
    Packet(const char* five_tuple);
    Ipv4Address getDstIpAddr()const;
    Ipv4Address getSrcIpAddr()const;
    String getDstIpAddrStr()const;
    String getSrcIpAddrStr()const;
    const uint8_t* getDstIpAddrBytes()const;
    const uint8_t* getSrcIpAddrBytes()const;
    UINT32_T getPktSize()const;
    String getMessage()const;
    String toString()const;
protected:
    //暂时不写MAC地址
    Ipv4Address _ipv4Src;
    Ipv4Address _ipv4Dst;
    char _sport[2];
    char _dport[2];
    char _protocol[1];
    UINT32_T _pktSize;
    String _msg; 
};
#endif